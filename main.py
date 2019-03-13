from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager, Screen
import datetime
import mysql.connector

now = datetime.datetime.now()

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='',
    database='symphony'
)


class MainManagement(ScreenManager):
    pass


class LoginScreen(Screen):
    pass


class MenuScreen(Screen):
    pass


class SalesScreen(Screen):
    pass


class ScannerScreen(Screen):

    #   this method is called as soon the button "Add to Cart" is pressed
    def add_cart(self):
        p_code = self.ids.code_inp.text

        product_name = mydb.cursor()
        sqlFormulaGetName = 'SELECT product_name FROM product WHERE product_id = %s'
        product_name.execute(sqlFormulaGetName, (p_code,))
        p_name = product_name.fetchone()
        print(p_name[0])

        p_qtd = self.ids.qty_inp.text

        product_price = mydb.cursor()
        sqlFormulaGetPrice = 'SELECT price_sell FROM product WHERE product_id = %s'
        product_price.execute(sqlFormulaGetPrice, (p_code,))
        p_un_price = product_price.fetchone()
        print(p_un_price[0])

        p_total = str(round(int(p_qtd) * float(p_un_price[0]), 2))

        last_receipt = mydb.cursor()
        last_receipt.execute("SELECT MAX(receipts_no) FROM saved_receipts")
        result = last_receipt.fetchone()

        products_container = self.ids.cart_win

        details = BoxLayout(size_hint_y=None, height=30, pos_hint={'top': 1})
        products_container.add_widget(details)

        code = Label(text=p_code, size_hint_x=0.2, color=(0.06, 0.45, 0.45, 1))
        name = Label(text=str(p_name[0]), size_hint_x=0.3, color=(0.06, 0.45, 0.45, 1))
        qty = Label(text=p_qtd, size_hint_x=0.1, color=(0.06, 0.45, 0.45, 1))
        un_price = Label(text='€ ' + str(p_un_price[0]), size_hint_x=0.1, color=(0.06, 0.45, 0.45, 1))
        total = Label(text='€ ' + p_total, size_hint_x=0.2, color=(0.06, 0.45, 0.45, 1))

        details.add_widget(code)
        details.add_widget(name)
        details.add_widget(qty)
        details.add_widget(un_price)
        details.add_widget(total)

        # cursor is the object that communicate with your SQL server
        insertInto = mydb.cursor()

        #  sqlFormula create a SQL Query
        #  %s work as placeholders, these placeholders can be replaced by any value
        sqlFormula = "INSERT INTO scanned_products (receipt, product_code, product_name, quantity, unit_price, " \
                     "total_price, date)" \
                     "VALUES (%s, %s, %s, %s, %s, %s, %s)"

        sales = [(int(result[0] + 1), p_code, str(p_name[0]), p_qtd, str(p_un_price[0]), p_total, now)]

        insertInto.executemany(sqlFormula, sales)

        mydb.commit()

    #   this method is called as soon the button "SAVE" is pressed
    @staticmethod
    def save_open_receipt():
        # cursor is the object that communicate with your SQL server
        myCursor = mydb.cursor()

        #    execute is the object that runs the MySQL Query
        myCursor.execute('CALL save_open_receipts()')
        #   mycursor.execute('SELECT age FROM student')

        # fetchall function means that it will fetch all the rows in the execution statement
        print('SAVED')
        mydb.commit()

    #   this method is called as soon the button "CheckOut" is pressed
    @staticmethod
    def save_checkout_receipt():
        # cursor is the object that communicate with your SQL server
        myCursor = mydb.cursor()

        #    execute is the object that runs the MySQL Query
        myCursor.execute('CALL save_checkout_receipts()')
        #   mycursor.execute('SELECT age FROM student')

        # fetchall function means that it will fetch all the rows in the execution statement
        print('SAVED')
        mydb.commit()

    #   this method is called as soon the button "Accounts" is pressed
    def save_account_receipt(self):
        account_number = self.ids.account_no_scanner.text
        # cursor is the object that communicate with your SQL server
        myCursor = mydb.cursor()

        sqlFormulaSaveAccount = 'CALL save_account_receipts(%s)'

        #    execute is the object that runs the MySQL Query
        myCursor.execute(sqlFormulaSaveAccount, (account_number,))

        mydb.commit()


class OpenReceipts(Screen):

    #   this method is called as soon the button "Update" is pressed
    def show_open_receipts(self):
        products_container = self.ids.receipts_open

        showReceipts = mydb.cursor()
        showReceipts.execute("SELECT * FROM saved_receipts WHERE situation = 1")
        result = showReceipts.fetchall()

        for row in result:
            details = BoxLayout(size_hint_y=None, height=30, pos_hint={'top': 1})
            products_container.add_widget(details)

            code = Label(text=str(row[0]), size_hint_x=0.3, color=(0.06, 0.45, 0.45, 1))
            date = Label(text=str(row[1]), size_hint_x=0.4, color=(0.06, 0.45, 0.45, 1))
            description = Label(text=str(row[2]), size_hint_x=0.4, color=(0.06, 0.45, 0.45, 1))
            total_price = Label(text=str(row[3]), size_hint_x=0.3, color=(0.06, 0.45, 0.45, 1))

            details.add_widget(date)
            details.add_widget(code)
            details.add_widget(description)
            details.add_widget(total_price)

    def update_receipt_toAccount(self):
        rec_no = self.ids.receipt_no.text
        acct_no = self.ids.account_no_receipts.text

        updateAccount = mydb.cursor()

        #    execute is the object that runs the MySQL Query
        sqlFormula = 'UPDATE saved_receipts SET situation = 3, account_number = %s' \
                     ' WHERE receipts_no = %s'

        updateAccount.execute(sqlFormula, (str(acct_no,), str(rec_no,)))

        mydb.commit()

    def update_receipt_toCheckOut(self):
        rec_no = self.ids.receipt_no.text

        updateAccount = mydb.cursor()

        #    execute is the object that runs the MySQL Query
        sqlFormula = 'UPDATE saved_receipts SET situation = 2 WHERE receipts_no = %s'

        updateAccount.execute(sqlFormula, (rec_no,))

        mydb.commit()


class ReceiptList(Screen):

    #   this method is called as soon the button "Update" is pressed
    def show_receipts(self):
        products_container = self.ids.all_receipts

        showReceipts = mydb.cursor()
        showReceipts.execute("SELECT * FROM saved_receipts WHERE situation > 1")
        result = showReceipts.fetchall()

        for row in result:
            details = BoxLayout(size_hint_y=None, height=30, pos_hint={'top': 1})
            products_container.add_widget(details)

            code = Label(text=str(row[0]), size_hint_x=0.2, color=(0.06, 0.45, 0.45, 1))
            date = Label(text=str(row[1]), size_hint_x=0.3, color=(0.06, 0.45, 0.45, 1))
            description = Label(text=str(row[2]), size_hint_x=0.3, color=(0.06, 0.45, 0.45, 1))
            total_price = Label(text=str(row[3]), size_hint_x=0.3, color=(0.06, 0.45, 0.45, 1))

            details.add_widget(date)
            details.add_widget(code)
            details.add_widget(description)
            details.add_widget(total_price)


class FinancesScreen(Screen):
    pass


class PayableScreen(Screen):

    #   this method is called as soon the button "Add a New Bill" is pressed
    def add_payable(self):
        p_code = self.ids.bank_inp.text
        p_cat = self.ids.cat_inp.text
        p_provider = self.ids.provider_inp.text
        p_date = self.ids.date_inp.text
        p_total = str(float(self.ids.total_inp.text))

        products_container = self.ids.bills_cart

        # if p_code != '':
        details = BoxLayout(size_hint_y=None, height=30, pos_hint={'top': 1})
        products_container.add_widget(details)
        # the variable details is add in to products_container

        code = Label(text=p_code, size_hint_x=0.15, color=(0.06, 0.45, 0.45, 1))
        Category = Label(text=p_cat, size_hint_x=0.2, color=(0.06, 0.45, 0.45, 1))
        provider = Label(text=p_provider, size_hint_x=0.15, color=(0.06, 0.45, 0.45, 1))
        date = Label(text=p_date, size_hint_x=0.2, color=(0.06, 0.45, 0.45, 1))
        total = Label(text='€' + p_total, size_hint_x=0.15, color=(0.06, 0.45, 0.45, 1))
        space = Label(text='', size_hint_x=0.2, color=(0.06, 0.45, 0.45, 1))

        details.add_widget(code)
        details.add_widget(Category)
        details.add_widget(provider)
        details.add_widget(date)
        details.add_widget(total)
        details.add_widget(space)

        insertInto = mydb.cursor()

        #  sqlFormula create a SQL Query
        #  %s work as placeholders, these placeholders can be replaced by any value
        sqlFormula = "INSERT INTO payable_table (bank_slip, category, provider, expire_date, total_price)" \
                     "VALUES (%s, %s, %s, %s, %s)"

        payable = [(p_code, p_cat, p_provider, p_date, p_total)]

        insertInto.executemany(sqlFormula, payable)

        mydb.commit()

    def show_bills(self):
        products_container = self.ids.bills_cart

        showBills = mydb.cursor()
        showBills.execute("SELECT * FROM payable_table")
        result = showBills.fetchall()

        for row in result:
            details = BoxLayout(size_hint_y=None, height=30, pos_hint={'top': 1})
            products_container.add_widget(details)

            bank_slip = Label(text=str(row[1]), size_hint_x=0.2, color=(0.06, 0.45, 0.45, 1))
            category = Label(text=str(row[2]), size_hint_x=0.35, color=(0.06, 0.45, 0.45, 1))
            provider = Label(text=str(row[3]), size_hint_x=0.2, color=(0.06, 0.45, 0.45, 1))
            expire_date = Label(text=str(row[4]), size_hint_x=0.3, color=(0.06, 0.45, 0.45, 1))
            total_price = Label(text=str(row[5]), size_hint_x=0.3, color=(0.06, 0.45, 0.45, 1))
            space = CheckBox(color=(0, 0, 0, 1), size_hint_x=0.2)

            details.add_widget(bank_slip)
            details.add_widget(category)
            details.add_widget(provider)
            details.add_widget(expire_date)
            details.add_widget(total_price)
            details.add_widget(space)


# class NewPayable(Screen):
#     pass
#
#
# class OpenPayableBills(Screen):
#     pass


class ReceivableScreen(Screen):
    #   this method is called as soon the button "Update" is pressed
    def show_receive_bills(self):
        products_container = self.ids.receivable_bills

        showReceiveBills = mydb.cursor()
        showReceiveBills.execute("SELECT * FROM saved_receipts WHERE situation > 1")
        result = showReceiveBills.fetchall()

        for row in result:
            details = BoxLayout(size_hint_y=None, height=30, pos_hint={'top': 1})
            products_container.add_widget(details)

            code = Label(text=str(row[0]), size_hint_x=0.2, color=(0.06, 0.45, 0.45, 1))
            date = Label(text=str(row[1]), size_hint_x=0.3, color=(0.06, 0.45, 0.45, 1))
            description = Label(text=str(row[2]), size_hint_x=0.3, color=(0.06, 0.45, 0.45, 1))
            total_price = Label(text=str(row[3]), size_hint_x=0.3, color=(0.06, 0.45, 0.45, 1))

            details.add_widget(date)
            details.add_widget(code)
            details.add_widget(description)
            details.add_widget(total_price)


class ManagementScreen(Screen):
    pass


class CustomerScreen(Screen):

    def save_Customer(self):
        pps_No = self.ids.pps_inp.text
        p_Fname = self.ids.name_inp.text
        p_Lname = self.ids.surname_inp.text
        p_phone1 = self.ids.phone_inp.text
        p_phone2 = self.ids.phone2_inp.text
        p_address = self.ids.address_inp.text
        p_street = self.ids.street_inp.text
        p_city = self.ids.city_inp.text
        p_email = self.ids.email_inp.text
        p_credit = self.ids.credit_inp.text

        insertIntoCustomer = mydb.cursor()

        #  sqlFormula create a SQL Query
        #  %s work as placeholders, these placeholders can be replaced by any value
        sqlFormulaCustomer = "INSERT INTO customers " \
                             "(pps_number, first_name, last_name, phone_number, phone_number_2, address, " \
                             "street_address, city, email, credit) " \
                             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        customer = [(pps_No, p_Fname, p_Lname, p_phone1, p_phone2, p_address, p_street, p_city,
                     p_email, p_credit)]

        insertIntoCustomer.executemany(sqlFormulaCustomer, customer)

        mydb.commit()


class ProviderScreen(Screen):

    def save_provider(self):
        national_no = self.ids.national_no.text
        p_name = self.ids.p_name_inp.text
        p_contact = self.ids.contact_inp.text
        p_p_phone1 = self.ids.p_phone_inp.text
        p_p_phone2 = self.ids.p_phone2_inp.text
        p_address = self.ids.p_address_inp.text
        p_street = self.ids.p_street_inp.text
        p_city = self.ids.p_city_ipn.text
        p_email = self.ids.p_email_inp.text

        insertIntoProvider = mydb.cursor()

        sqlFormulaProvider = "INSERT INTO provider " \
                             "(national_no, name, contact, phone_no, phone_no2, address, street_ad, city, email) " \
                             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        provider = [(national_no, p_name, p_contact, p_p_phone1, p_p_phone2, p_address, p_street, p_city, p_email)]

        insertIntoProvider.executemany(sqlFormulaProvider, provider)

        mydb.commit()


class ProductScreen(Screen):

    def save_product(self):
        category = self.ids.category_inp.text
        name = self.ids.pro_name_inp.text
        payed_price = self.ids.payed_price_inp.text
        provider = self.ids.pro_provider_inp.text
        price_sell = self.ids.price_sell_inp.text

        insertIntoProduct = mydb.cursor()

        sqlFormulaProduct = "INSERT INTO product " \
                            "(category, product_name, payed_price, provider, price_sell) " \
                            "VALUES (%s, %s, %s, %s, %s)"

        product = [(category, name, payed_price, provider, price_sell)]

        insertIntoProduct.executemany(sqlFormulaProduct, product)

        mydb.commit()


class ReportsScreen(Screen):
    pass


class Symphony1(App):
    def build(self):
        return MainManagement()


Symphony1().run()
