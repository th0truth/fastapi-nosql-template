from fastapi import APIRouter
from strawberry.fastapi import GraphQLRouter

from core.schemas.graphql import schema

router = APIRouter()

graphql_app = GraphQLRouter(schema, tags=["GraphQL"])