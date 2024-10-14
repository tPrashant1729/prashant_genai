from zenml.client import Client

artifact = Client().get_artifact_version('c86db30a-249e-4e45-bc40-09f55ce21534')
loaded_artifact = artifact.load()