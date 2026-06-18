import boto3
from core.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_REGION

dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION
)
table = dynamodb.Table("hash_table")

def save_hash(hash_file: str, s3_key: str):
    table.put_item(Item={"hash_file": hash_file, "s3_key": s3_key})

def get_all_hashes():
    # Devuelve todos los registros para agrupar en memoria
    response = table.scan()
    return response.get("Items", [])

def delete_hash_by_s3_key(s3_key: str):
    # Escanea para encontrar el hash_file asociado al s3_key y borrarlo
    response = table.scan(
        FilterExpression="s3_key = :k",
        ExpressionAttributeValues={":k": s3_key}
    )
    for item in response.get("Items", []):
        try:
            # Intenta borrar asumiendo hash_file como Partition Key y s3_key como Sort Key
            table.delete_item(Key={"hash_file": item["hash_file"], "s3_key": item["s3_key"]})
        except Exception:
            # Si falla, asume que hash_file es la única llave primaria
            table.delete_item(Key={"hash_file": item["hash_file"]})
