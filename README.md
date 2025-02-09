# Inventory-management
Clearer Database Structure: Uses a junction table (BranchStock) to explicitly manage the many-to-many relationship between products and branches.

Sales Targets: Added sales_target to the Branch model.  The stock distribution now uses these targets to allocate stock proportionally.

Proportional Distribution: The distribute_stocks function now calculates the stock to distribute to each branch based on its sales target relative to the total sales target of all branches.

Integer Stock: Stock levels are now treated as integers (using int() during distribution) since you can't have fractions of items.

Handles Zero Sales Targets: Includes a check for the case where the total sales target is zero. In this scenario, it defaults to an equal distribution of stock among branches to avoid division by zero errors. It also prints a warning message.

Handles Insufficient Stock: Prevents over-distribution of stock by checking if stock_to_distribute exceeds the remaining_stock.

Updates overall stock: The overall stock of the product is updated after distribution.

Commit after every product: The database changes are committed after the stock distribution for each product. This is important to prevent data inconsistencies if an error occurs during the distribution process for subsequent products.

Initialization of Branch Stock: The code now correctly initializes a BranchStock entry with a stock level of 0 if one doesn't already exist for a given product and branch combination. This prevents errors when trying to update a non-existent record.

Example Usage: Provides a more complete example of how to add products and branches and then call the distribute_stocks function.  It also demonstrates how to query and print the stock levels after distribution.

SQLite for Simplicity: Uses SQLite for demonstration purposes.

Relationship Management: Uses SQLAlchemy's relationship features (relationship()) and back_populates to manage the relationships between the models efficiently.  This makes it easy to access related data (e.g., getting the branch of a branch stock).

This revised version provides a much more robust and practical implementation of the stock distribution system.  It addresses the key issues and incorporates best practices for database design and SQLAlchemy usage.