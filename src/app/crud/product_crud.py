from .base_crud import BaseCRUD

class ProductCRUD(BaseCRUD):
  def __init__(self, db):
    super().__init__(db)
  
  