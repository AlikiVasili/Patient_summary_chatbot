import sys
import requests
import json

PATIENT_IDENTIFIER_SYSTEM = "urn:oid:2.16.840.1.113883.3.9143.2.1.1"
GLOBAL_FHIR_URL = "https://dev-fhir.ehealth4u.eu/fhir/"
KEYCLOAK_ACCESS_URL = "https://auth.3ahealth.com"
KEYCLOAK_REALM = "ehealth4u"
KEYCLOAK_TOKEN_PATH = "protocol/openid-connect/token"
KEYCLOAK_FULL_URL = f"{KEYCLOAK_ACCESS_URL}/realms/{KEYCLOAK_REALM}/{KEYCLOAK_TOKEN_PATH}"
KEYCLOAK_CLIENT_ID = "ehealth4u-ehr"
KEYCLOAK_CLIENT_SECRET = "0ZV4EkWlX3PrX2oif9MZVTCBHZthXpQZ"
KEYCLOAK_GRANT_TYPE = "password"
KEYCLOAK_USERNAME = "patient"
KEYCLOAK_PASSWORD = "patient"
KEYCLOAK_SCOPE = "fhir"


def generateNewToken():
    # Define the body
    body = {
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "grant_type": KEYCLOAK_GRANT_TYPE,
        "username": KEYCLOAK_USERNAME,
        "password": KEYCLOAK_PASSWORD,
        "scope": KEYCLOAK_SCOPE
    }

    # Try to get the token
    try:
        response = requests.post(KEYCLOAK_FULL_URL, data=body)
        token = response.json()["access_token"]
    except Exception as e:
        print("Error getting token: " + str(e))
        return

    return token


def getPatientId(token, patient_identifier_value):
    # Define the url
    url = GLOBAL_FHIR_URL + "Patient?identifier=" + PATIENT_IDENTIFIER_SYSTEM + "|" + patient_identifier_value

    # Try to get the patient id
    try:
        response = requests.get(url, headers={"Authorization": "Bearer " + token})
        responseAsJson = response.json()
        patientId = responseAsJson["entry"][0]["resource"]["id"]
    except Exception as e:
        print("Error getting patient id: " + str(e))
        return

    return patientId


def getPatientSummary(token, patientId):
    # Define the url
    url = GLOBAL_FHIR_URL + "Patient/" + patientId + "/$summary"

    # Try to get the patient summary
    try:
        response = requests.get(url, headers={"Authorization": "Bearer " + token})
        patientSummary = response.json()
    except Exception as e:
        print("Error getting patient summary: " + str(e))
        return

    return patientSummary


# Define main
def main(patient_identifier_value):
    # Generate a new token
    token = generateNewToken()

    # Get the patient id
    patientId = getPatientId(token, patient_identifier_value)

    # Get the patient summary
    patientSummary = getPatientSummary(token, patientId)

    # Beautify the patient summary
    beautifiedPatientSummary = json.dumps(patientSummary, indent=4)

    # Save the patient summary to file
    with open("patientSummary.json", "w") as file:
        file.write(str(beautifiedPatientSummary))

    # Return the patientId
    return patientId


if __name__ == "__main__":
    # Check if the PATIENT_IDENTIFIER_VALUE is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python get_patient_summary.py <PATIENT_IDENTIFIER_VALUE>")
        sys.exit(1)

    # Extract the patient identifier value from the command-line argument
    patient_identifier_value = sys.argv[1]

    # Call main with the provided patient_identifier_value
    returned_patientId = main(patient_identifier_value)

    # Now you can use returned_patientId in the calling program
    print(returned_patientId)
