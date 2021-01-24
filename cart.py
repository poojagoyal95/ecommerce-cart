import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()

class CommonClass:
    def dbConnection():
        # establish connection with databse
        mydb = mysql.connector.connect(
            host = os.getenv("HOST"),
            user = os.getenv("DB_USERNAME"),
            password =os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_DATABASE")
        )
        return  mydb.cursor() ,mydb

    def validateInput(text,type):
        try:
            userOption = type(input(text))
            print(userOption)
            if not userOption:
                CommonClass.validateInput(text,type)                 
            else:
                return userOption

        except Exception as e:
            CommonClass.validateInput(text,type)
           

    def startProcess():
        # chhose option you are admin or user     
        userOption = CommonClass.validateInput("Select option whether you are admin or user. Enter \n 1 - Admin \n 2 - User \n",int)
        if userOption == 1:
            print("Welcome to Admin Section")
            Admin()
        elif userOption == 2:
            User()    
        else:
            CommonClass.startProcess() 
        

    def getCategoryQuery(self):
        #query to get categories from table
        self.connection.execute("SELECT id,name FROM category")
        res = self.connection.fetchall()    
        return res    

    def getProductByCategory(self,category):
        #query to get product on basis of category
        self.connection.execute("SELECT name,description,price FROM product where category_id = (select id from category where name = %s)",(category,))
        res = self.connection.fetchall()   
        return res        

class User:
    def __init__(self):
        print("Welcome To users Section")
        self.connection,self.db = CommonClass.dbConnection()
        self.userId = 0
        self.checkName()

    def checkName(self):
        # check whther user exists or not
        name = CommonClass.validateInput("Enter User Name ?",str)
        self.connection.execute("SELECT id FROM user where name = %s",(name,))
        res = self.connection.fetchone()
        if res is None:
            print("This User not exists , so we are creating user of this name")
            self.connection.execute("""INSERT INTO user (name) VALUES (%s)""",(name,))
            self.db.commit()
            self.userId = self.connection.lastrowid
            print("User is sucessfully added")
        else:
            print("user exists")
            self.userId = res[0]
        print("user login successfully")
        self.showCategory()    
            

    def getProductId(self,categoryId):
        # get id of product by entering category and product
        product = CommonClass.validateInput("Enter product name \n",str)
        quantity = CommonClass.validateInput("Enter quantity of above product \n",int)

        if quantity > 0:
        
            self.connection.execute("SELECT id FROM product where category_id = %s and name = %s",(categoryId,product))
            status = self.connection.fetchone()
            if status is None:
                print("Please add valid product")
                self.getProductId(categoryId)
            else:
                self.connection.execute("SELECT id,quantity FROM cart where product_id = %s",(status[0],))
                res = self.connection.fetchone()
                if res is None:
                    self.connection.execute("""INSERT INTO cart (user_id,product_id,quantity) VALUES (%s,%s,%s)""",(self.userId,status[0],quantity))
                else:
                    self.connection.execute("""UPDATE cart SET quantity = %s WHERE product_id = %s""",(res[1]+quantity,status[0]))
                self.db.commit()

            option = CommonClass.validateInput("Do you want add more products \n 1 - add more for same category \n 2- for different category \n 3 - Back to user menu \n",int)
            if option == 1:
                self.getProductId(categoryId)
            elif option == 2:
                self.addProductToCart()
            else:
                self.showCategory()   
        else:
            self.getProductId(categoryId)                  

    def addProductToCart(self):
        # add product to cart
        print("addd product to cart")
        category = CommonClass.validateInput("Enter category for products \n",str)

        status = Admin.checkCategory(self,category)
        if status is None:
            print("Please add valid category with below listed categories")
            res = CommonClass.getCategoryQuery(self)
            print(res)
            self.addProductToCart()
        else:
            print("select product you want to added in cart")
            res = CommonClass.getProductByCategory(self,category)
            result = {}
            if (len(res) > 0):
                for r in res:
                    result['name'] = r[0]
                    result['description'] = r[1]
                    result['price'] = r[2]
                print(result)
                self.getProductId(status[0])
            else:
                print("No Product found!! Select other category")
                self.addProductToCart()  
    
    def checkOutItems(self,result):
        # checkout items from means bill is published for user
        amount = 0
        for r in result:
            amount = amount+(r[5]*r[3])
        self.connection.execute("""INSERT INTO orders (user_id,total_amount) VALUES (%s,%s)""",(self.userId,amount))
        self.db.commit()
        orderId = self.connection.lastrowid
        res = []
        for r in result:
            res.append((orderId,r[0],r[5],r[3]*r[5]))
        self.connection.executemany("""INSERT INTO order_product (order_id,product_id,quantity,amount) VALUES (%s,%s,%s,%s)""",res)
        self.db.commit()   

        self.connection.execute("""DELETE FROM cart WHERE user_id = %s""",(self.userId,))
        self.db.commit()
        
        if amount > 10000:
            amount = amount-500
            self.connection.execute("""UPDATE orders SET discount = %s , total_amount = %s , status = %s WHERE user_id = %s and status = 1 """,(500,amount,0,self.userId))
            self.db.commit()
        print("You bill is successfully placed!! Thanks with total amount " + str(amount))

        option = CommonClass.validateInput("Enter option \n 1 - Back to users menu section \n 2 - logout \n",int)

        if option ==1:
            self.showCategory()
        else:
            CommonClass.startProcess()    

    def removeValueFromCart(self,res):
        # update value from cart
        for r in res:
            print("product name : "+str(r[1]) +" description : "+str(r[2]) +" price : " + str(r[3]) + " category name : "+str(r[4]) + " quantity : "+str(r[5]) )

        category = CommonClass.validateInput("Enter category name \n",str)
        product = CommonClass.validateInput("Enter product name \n",str)
        quantity = CommonClass.validateInput("Enter quantity you want to update \n",int)
        if quantity > 0:
            for r in res:
                if r[1] == product and r[4] == category:
                    self.connection.execute("""UPDATE cart SET quantity = %s WHERE product_id = %s """,(quantity,r[0]))
                    self.db.commit()
                    break
                else:
                    print("Value not exists .Please enter valid values")
                    self.removeValueFromCart(res)

            option = CommonClass.validateInput("Enter option \n 1 - show cart \n 2 - back to User Menu",int)
            if option ==1 :
                self.cartProces()
            else:
                self.showCategory()
        else:
            self.removeValueFromCart(res)               

    def cartProces(self):
        # show the listing of values in cart
        self.connection.execute("SELECT id FROM cart where user_id = %s",(self.userId,))
        res = self.connection.fetchall()        
        if len(res) > 0:
            cart = {}
            result = []
            self.connection.execute("SELECT p.id,p.name as product_name ,p.description,p.price,cat.name as category_name,c.quantity FROM cart as c ,product as p , category as cat where c.product_id = p.id and p.category_id = cat.id and c.user_id = %s",(self.userId,))
            res = self.connection.fetchall()
            for r in res:
                print("product name : "+str(r[1]) +" description : "+str(r[2]) +" price : " + str(r[3]) + " category name : "+str(r[4]) + " quantity : "+str(r[5]) )

            option = CommonClass.validateInput("Enter option \n 1 - remove value from cart \n 2 - Checkout cart Items \n 3 - Back to user section \n",int)

            if option == 1:
                self.removeValueFromCart(res)
            elif option == 2:
                self.checkOutItems(res)
            elif option ==3:
                self.showCategory()
            else:
                self.cartProces()
        else:
            print("No value added in cart")
            option = CommonClass.validateInput("Select Option \n 1- Add values to Cart \n 2- Show User Menu",int)

            if option == 1:
                self.addProductToCart()
            elif  option == 2:
                self.showCategory()
            else:
                self.cartProces()       

    def showCategory(self):
        # show categories
        res = CommonClass.getCategoryQuery(self)    
        if (len(res) > 0):
            print("List of categories are listed below")
            print(res)

            option = CommonClass.validateInput("Enter option you want to search for \n 1 - see products of category \n 2 - Add product to Cart \n 3 - Show Cart \n 4 - Back to Main Menu \n",int)

            if option == 1:
                self.showProduct()
            elif option  ==2:
                self.addProductToCart()    
            elif  option == 3:
                self.cartProces()    
            elif option == 4:
                CommonClass.startProcess()  
            else:
                self.showCategory()      
        else:
            print("No Category found!!")
            CommonClass.startProcess()  

    def showProduct(self):
        # show products
        print("Please enter category for which you want to see products")

        category = CommonClass.validateInput("Enter Category \n",str)

        res = CommonClass.getProductByCategory(self,category)
        result ={}     
        if (len(res) > 0):
            for r in res:
                result['name'] = r[0]
                result['description'] = r[1]
                result['price'] = r[2]
            print(result)

            option = CommonClass.validateInput("Enter option \n 1- add products to cart \n 2 - show cart  \n 3- Back To User menu \n",int)
            if option ==1:
                self.addProductToCart()
            elif option == 2:
                self.cartProces()
            elif option == 3:
                self.showCategory()
            else:
                self.showProduct()        

        else:
            print("No Product found!!")
            self.showCategory()  


class Admin:
    def __init__(self):
        print("Choose options: \n 1 - Categories / Products \n 2 - Users Cart Details \n 3 - Users Bill \n 4 - Redirect To User Section")

        option = CommonClass.validateInput("Enter option ?",int)

        self.connection,self.db = CommonClass.dbConnection()
        self.res = []
        if option == 1:
            self.CategoryProduct()
        elif option ==2:
            self.showUserCart()
        elif option ==3:
            self.showUserBill()        
        elif option == 4:
            User()
        else:
            Admin()

    def showUserCart(self):
        # show values added in cart by user
        userId = self.checkUserExists()
        self.connection.execute("SELECT id FROM cart where user_id = %s",(userId,))
        status =  self.connection.fetchone()
        
        if status is None:
            print("No value added in cart , User checkout its bill")
            
        else:
            self.connection.execute("SELECT p.id,p.name as product_name ,p.description,p.price,cat.name as category_name,c.quantity FROM cart as c ,product as p , category as cat where c.product_id = p.id and p.category_id = cat.id and c.user_id = %s",(self.userId,))
            res = self.connection.fetchall()
            for r in res:
                print("product name : "+str(r[1]) +" description : "+str(r[2]) +" price : " + str(r[3]) + " category name : "+str(r[4]) + " quantity : "+str(r[5]) )

        option = CommonClass.validateInput("Enter \n 1 - check for other user \n 2 - go to main admin process",int)

        if option ==1:
            self.showUserCart()
        else:
            Admin()

    def showUserBill(self):
        #show bill of user
        userId = self.checkUserExists()
        self.connection.execute("SELECT id FROM orders where user_id = %s",(userId,))
        res =  self.connection.fetchall()
        print(res)
        if len(res) > 0:
            self.connection.execute("SELECT sum(total_amount) FROM `orders` where user_id = %s",(userId,))
            res = self.connection.fetchone()
            print("Summary of Bill :  "+str(res[0]))
            
        else:
            print("No bill found for user")

        option = CommonClass.validateInput("Enter \n 1 - check for other user \n 2 - go to main admin process",int)  
        if option ==1:
            self.showUserBill()
        else:
            Admin()        

    def checkUserExists(self):
        # check user exixts or not
        name = CommonClass.validateInput("Enter User Name \n",str) 

        self.connection.execute("SELECT id FROM user where name = %s",(name,))
        status =  self.connection.fetchone()
        if status is None:
            print("user not exists , Enter valid user name")
            self.checkUserExists()
        else:
            return status[0]   

    def addProduct(self,category_id):
        # add product to databse
        name = CommonClass.validateInput("Enter Name \n",str)
        desc = CommonClass.validateInput("Enter description \n",str)
        price = CommonClass.validateInput("Enter price \n",int)

        self.res.append((name,desc,price,category_id))

        askAgain = CommonClass.validateInput("Do you want to add more?\n 1- yes \n 2- no\n",int)

        if askAgain == 1:
            self.addProduct(category_id)
        else:
            self.connection.executemany("""INSERT INTO product (name,description,price,category_id) VALUES (%s,%s,%s,%s)""",self.res)
            self.db.commit()
        print("Products added sucessfully")    

    def addCategory(self,category):
        # add category to databse
        self.connection.execute("""INSERT INTO category (name) VALUES (%s)""",(category,))
        self.db.commit()
        return self.connection.lastrowid

    def checkCategory(self,category):
        #check vategory exists or not
        self.connection.execute("SELECT id FROM category where name = %s",(category,))
        return self.connection.fetchone()

    def CategoryProduct(self):
        #add product under category
        print("Do you want add category or add products in category? \n 1 - Category \n 2 - Product")

        option = CommonClass.validateInput("Enter option \n",int)
        if option == 1:
            category = CommonClass.validateInput("Enter Category Name? \n",str)

            status = self.checkCategory(category)
            if status is None:
                id = self.addCategory(category)
                print("Category is sucessfully added and add products for same")
                self.addProduct(id)
            else:
                option = CommonClass.validateInput("Category already exists , you want to \n 1 - add products \n 2 - add different category \n",int)

                if option == 1:
                    self.addProduct(status[0])
                else:
                    self.addCategory()   
        elif option ==2:        
            category = CommonClass.validateInput("Enter category for which you want to add products?\n",str)
            status = self.checkCategory(category)
            if status is None:
                print("This category not exists , so we are creating category of this name")
                id = self.addCategory(category)
                print("Category is sucessfully added and add products for same")
                self.addProduct(id)
            else:
                print("category exists , you can add products for same")
                self.addProduct(status[0])
        else:
            print("Please add valid option")
            self.CategoryProduct() 

        Admin()
           
CommonClass.startProcess()
    






  
