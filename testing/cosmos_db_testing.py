# NOSql testing with local cosmos DB emulator
from azure.cosmos import CosmosClient, PartitionKey

points = [(0,0), (1, 2), (3, 5), (3, 7)]
x_coords = [point[0] for point in points]
y_coords = [point[1] for point in points]

client = CosmosClient(
    url="https://localhost:8081",
    credential=(
        "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGG"
        "yPMbIZnqyMsEcaGQy67XIw/Jw=="
    ),
)

print('connected ...')
database = client.create_database_if_not_exists(
    id="cosmos_works",
    offer_throughput=400,
)

container = database.create_container_if_not_exists(
    id="products3",
    partition_key=PartitionKey(
        path="/category",
    ),
)

item = {"id": "6800000001", "name": "Kiama classic surfboard", "summary": "desdc1 updated", "price": 1200}
item2 = {"id": "6800000002", "name": "Tesla classic surfboard", "summary": "desdc2 "}
container.upsert_item(item)
# container.upsert_item(item2)
items = container.query_items('SELECT * FROM products3',
                              enable_cross_partition_query=True)

for item in items:
    print(item)

print(f"the type: {type(item)}")

print ('database updated..')