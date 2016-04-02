import graphene
from todos import schema as todosSchema

class Query(todosSchema.Query):
    pass

schema = graphene.Schema(name="Autodo.us Schema")
schema.query = Query