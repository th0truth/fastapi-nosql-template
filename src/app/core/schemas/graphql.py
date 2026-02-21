import strawberry
from typing import List, Optional
from api.graphql.resolvers import (
  get_users,
  get_user,
  get_products
)

@strawberry.type
class UserProfile:
  username: str
  email: str
  role: str

@strawberry.type
class Product:
  category: str
  item: str
  brand: str
  title: str
  price: int

@strawberry.type
class Query:
  @strawberry.field
  def hello(self) -> str:
    return "Hello world"
    
  @strawberry.field
  async def users(self, role: str) -> List[UserProfile]:
    users_data = await get_users(role)
    return [UserProfile(
      username=u.get("username"),
      email=u.get("email"),
      role=u.get("role")
    ) for u in users_data]

  @strawberry.field
  async def user(self, username: str) -> Optional[UserProfile]:
    if (u := await get_user(username)):
      return UserProfile(
        username=u.get("username"),
        email=u.get("email"),
        role=u.get("role")
      )
    return None

  @strawberry.field
  async def products(self, category: str) -> List[Product]:
    products_data = await get_products(category)
    return [Product(
      category=p.get("category"),
      item=p.get("item"),
      brand=p.get("brand"),
      title=p.get("title"),
      price=p.get("price")
    ) for p in products_data]
  
schema = strawberry.Schema(query=Query)