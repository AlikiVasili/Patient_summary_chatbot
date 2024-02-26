import pandas as pd
from sklearn.calibration import LabelEncoder
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from transformers import AdamW, get_linear_schedule_with_warmup
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

class TextClassificationDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        encoding = self.tokenizer(text, return_tensors='pt', max_length=self.max_length, padding='max_length', truncation=True)
        return {'input_ids': encoding['input_ids'].flatten(), 'attention_mask': encoding['attention_mask'].flatten(), 'label': torch.tensor(label)}

class BERTClassifier(nn.Module):
    def __init__(self, bert_model_name, num_classes):
        super(BERTClassifier, self).__init__()
        self.bert = AutoModel.from_pretrained(bert_model_name)
        self.dropout = nn.Dropout(0.1)
        self.fc = nn.Linear(self.bert.config.hidden_size, num_classes)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        x = self.dropout(pooled_output)
        logits = self.fc(x)
        return logits
    
    def train(self, data_loader, optimizer, scheduler, device):
        for batch in data_loader:
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            outputs = self(input_ids=input_ids, attention_mask=attention_mask)
            loss = nn.CrossEntropyLoss()(outputs, labels)
            loss.backward()
            optimizer.step()
            scheduler.step()

    def evaluate(self, data_loader, device):
        predictions = []
        actual_labels = []
        with torch.no_grad():
            for batch in data_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['label'].to(device)
                outputs = self(input_ids=input_ids, attention_mask=attention_mask)
                _, preds = torch.max(outputs, dim=1)
                predictions.extend(preds.cpu().tolist())
                actual_labels.extend(labels.cpu().tolist())
        return accuracy_score(actual_labels, predictions), classification_report(actual_labels, predictions, zero_division=1)

    
    def predict_sentiment(text, model, tokenizer, device, max_length=128):
        model.eval()
        encoding = tokenizer(text, return_tensors='pt', max_length=max_length, padding='max_length', truncation=True)
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)

        with torch.no_grad():
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                _, preds = torch.max(outputs, dim=1)
        return "positive" if preds.item() == 1 else "negative"

def load_data(data_file):
    df = pd.read_csv(data_file)

    inputs = df['input'].tolist()
    labels = df['intent'].tolist()

    return inputs, labels

def main(): 
    # read the train set
    data_file = "train_shuffled.csv"
    input, labels = load_data(data_file)
    print("Train dataset loaded and readed sucessfully!")

    # Set up parameters
    #bert_model_name = 'bert-base-uncased'
    # Use BioBERT model
    bert_model_name = 'dmis-lab/biobert-v1.1'
    num_classes = 11
    max_length = 128
    batch_size = 16
    num_epochs = 10
    learning_rate = 2e-5

    # Use label encoding to convert string labels to numerical labels
    label_encoder = LabelEncoder()
    labels = label_encoder.fit_transform(labels)

    # split the data
    train_texts, val_texts, train_labels, val_labels = train_test_split(input, labels, test_size=0.1, random_state=0)

    # initialise tockenizer, dataset, and data loader
    #tokenizer = BertTokenizer.from_pretrained(bert_model_name)
    # Initialize the BioBERT tokenizer
    tokenizer = AutoTokenizer.from_pretrained(bert_model_name)
    train_dataset = TextClassificationDataset(train_texts, train_labels, tokenizer, max_length)
    val_dataset = TextClassificationDataset(val_texts, val_labels, tokenizer, max_length)
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=batch_size)

    # set up device and model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = BERTClassifier(bert_model_name, num_classes).to(device)

    # set up optimizer and learning rate scheduler 
    optimizer = AdamW(model.parameters(), lr=learning_rate)
    total_steps = len(train_dataloader) * num_epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    # training the model
    for epoch in range(num_epochs):
        print(f"Epoch {epoch + 1}/{num_epochs}")
        model.train(train_dataloader, optimizer, scheduler, device)
        accuracy, report = model.evaluate(val_dataloader, device)
        print(f"Validation Accuracy: {accuracy:.4f}")
        print(report)

    # save the final model
    torch.save(model.state_dict(), "bio_bert_classifier.pth")


if __name__ == "__main__":
    main()