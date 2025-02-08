from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import ForeignKey

# Database configuration
DATABASE= "sqlite:///warehouse.db"
engine = create_engine(DATABASE)
Base = declarative_base()

# create table
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    unit_price = Column(Float)
    stock_level = Column(Integer)  # Overall stock in the warehouse
    
    def __int__(self,id,name,unit_price,stock_level):
        self.id=id
        self.name=name
        self.unit_price=unit_price
        self.stock_level=stock_level
        
        def __repr__(self):
          return f"({self.id}) {(self.name)} {(self.unit_price)}{(self.stock_level)}"
        
    # Relationship to branch stocks (back_populates for two-way relationship)
    branch_stocks = relationship("BranchStock", back_populates="product")

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    sales_target = Column(Integer) # : weekly sales target
    def __int__(self,id,name,sales_target):
        self.id=id
        self.name=name
        self.sales_target=sales_target
        def __repr__(self):
          return f"({self.id}) {(self.name)} {(self.sales_target)}"
        
    # Relationship to branch stocks (back_populates for two-way relationship)
    branch_stocks = relationship("BranchStock", back_populates="branch")

class BranchStock(Base):  # Junction table for many-to-many relationship
    __tablename__ = "branch_stocks"
    product_id = Column(Integer, ForeignKey ("products.id"), primary_key=True)
branch_id = Column(Integer, ForeignKey ("branches.id"), primary_key=True)
stock_level = Column(Integer) #stock at this branch

def __init(self,product_id,branch_id):
        self.product_id=product_id
        self.branch_id=branch_id
    
        def __repr__(self):
          return f"({self.product.id}) {(self.branch.id)}"
      
product = relationship("Product", back_populates="branch_stocks")
branch = relationship("Branch", back_populates="branch_stocks")



# Create tables
Base.metadata.create_all(bind=engine)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def distribute_stocks(db: sessionmaker):
    """Distributes stock to branches based on sales targets and current stock."""

    products = db.query(Product).all()
    branches = db.query(Branch).all()

    for product in products:
        total_sales_target = sum(branch.sales_target for branch in branches)

        if total_sales_target == 0:  # Handle the case where sales targets are all zero.
             print(f"Warning: Total sales target for {product.name} is zero.  Distributing equally.")
             equal_share = product.stock_level // len(branches) if len(branches) > 0 else 0
             for branch in branches:
                branch_stock = db.query(BranchStock).filter(BranchStock.product_id == product.id, BranchStock.branch_id == branch.id).first()
                if not branch_stock:
                    branch_stock = BranchStock(product_id=product.id, branch_id=branch.id, stock_level=0)  # Initialize if not exists
                    db.add(branch_stock)

                branch_stock.stock_level = equal_share
             product.stock_level = 0 # set overall stock to zero as it is distributed.

        else:
            remaining_stock = product.stock_level

            for branch in branches:
                # Proportionate distribution: (branch sales target / total sales target) * available stock
                distribution_percentage = branch.sales_target / total_sales_target
                stock_to_distribute = int(remaining_stock * distribution_percentage)  # Integer stock

                if stock_to_distribute > remaining_stock:  # Don't take more than available
                    stock_to_distribute = remaining_stock
                    
                branch_stock = db.query(BranchStock).filter(BranchStock.product_id == product.id, BranchStock.branch_id == branch.id).first()
                if not branch_stock:
                    branch_stock = BranchStock(product_id=product.id, branch_id=branch.id, stock_level=0)  # Initialize if not exists
                    db.add(branch_stock)
                
                branch_stock.stock_level += stock_to_distribute
                remaining_stock -= stock_to_distribute
            product.stock_level = remaining_stock # update overall stock

        db.commit() # commit changes for every product.

# Example usage:
db = SessionLocal()

# Add some products and branches (if they don't exist)
product1 = Product(name="Laptop", unit_price=25000.00, stock_level=100)
product2 = Product(name="Mouse", unit_price=750.00, stock_level=2000)
db.add_all([product1, product2])
db.commit()

branch1 = Branch(name="Nairobi", sales_target=50)
branch2 = Branch(name="Mombasa", sales_target=30)
branch3 = Branch(name="Kisumu", sales_target=20)
branch4 = Branch(name="Nakuru", sales_target=0) 
db.add_all([branch1, branch2, branch3, branch4])
db.commit()

distribute_stocks(db)

# Query and print branch stocks after distribution
for product in db.query(Product).all():
    print(f"Product: {product.name} (Warehouse Stock: {product.stock_level})")
    for branch_stock in product.branch_stocks:
        print(f"  Branch: {branch_stock.branch.name}, Stock: {branch_stock.stock_level}")

SessionLocal.close()