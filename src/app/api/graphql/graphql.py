from core.schemas.graphql import schema
from fastapi import APIRouter
from strawberry.fastapi import GraphQLRouter

router = APIRouter()

graphql_app = GraphQLRouter(schema, tags=["GraphQL"])
