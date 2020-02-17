import os
import sqlite3
from tempfile import mkdtemp

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd


# Specification https://cs50.harvard.edu/x/2020/tracks/web/finance/
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db", connect_args={'check_same_thread': False})

# Make sure API key is set
# Should get token there https://iexcloud.io/cloud-login#/
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    stocks = db.execute("""
        select symbol, name, sum(shares) shares, min(price) price,
               sum(shares) * min(price) total
          from transactions
         where user_id = :user_id
         group by symbol, name""", user_id=session["user_id"])
    balance_account = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["cash"]
    return render_template("index.html", stocks=stocks, balance_account=balance_account)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == 'GET':
        return render_template("buy.html")
    else:
        if not request.form.get("symbol"):
            return apology("missing symbols", 400)
        if not request.form.get("shares"):
            return apology("missing shares", 400)

        # user account balance
        user_cash_remaining = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])[0][
            'cash']

        # get share price
        share_data = lookup(request.form.get("symbol"))
        price_per_share = share_data["price"]

        # Calculate the price of requested shares
        total_price = price_per_share * int(request.form.get("shares"))

        if total_price > user_cash_remaining:
            return apology("CAN'T AFFORD", 400);

        con = sqlite3.connect('finance.db')
        try:
            with con:
                con.execute("update users set cash = cash - ? where id = ?", (total_price, session["user_id"]))
                con.execute("insert into transactions (user_id, name, symbol, shares, price) values (?, ?, ?, ?, ?)",
                            (session["user_id"], share_data["name"], share_data["symbol"],
                             request.form.get("shares"), price_per_share))
                flash("Bought")
        except sqlite3.Error as e:
            print('Transaction failed.', e)

        con.close()
        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute(
        "select symbol, shares, price, trans_date from transactions where user_id = :user_id order by trans_date desc",
        user_id=session["user_id"])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == 'GET':
        return render_template("quote.html")
    else:
        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        shares_data = lookup(request.form.get("symbol"))
        if not shares_data:
            return apology("invalid symbol", 400)
        return render_template("quote.html",
                               shares_data=f"{shares_data['name']} ({shares_data['symbol']}) costs ${shares_data['price']}")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == 'POST':
        new_user_id = db.execute("insert into users(username, hash) values(?, ?)",
                                 request.form.get("username"),
                                 generate_password_hash(password=request.form.get("password"), method='pbkdf2:sha512',
                                                        salt_length=14))

        # Remember which user has logged in
        session["user_id"] = new_user_id
        flash("Registered!")
        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    sell_data = db.execute(
        "select symbol, sum(shares) shares from transactions where user_id = :user_id group by symbol",
        user_id=session["user_id"])

    if request.method == 'GET':
        return render_template("sell.html", sell_data=sell_data)
    else:
        share_data = lookup(request.form.get("symbol"))
        if not request.form.get("symbol"):
            return apology("MISSING SYMBOL", 400)

        if request.form.get("shares") == "":
            return apology("MISSING SHARES", 400)

        # Check if the user have enough shares
        if len(sell_data) != 0 and int(request.form.get("shares")) > next(
                x['shares'] for x in sell_data if x['symbol'] == request.form.get("symbol")):
            return apology("TOO MANY SHARES", 400)

        price_per_share = share_data["price"]
        # Calculate the price of requested shares
        total_price = price_per_share * int(request.form.get("shares"))

        con = sqlite3.connect('finance.db')
        try:
            with con:
                con.execute("update users set cash = cash + ? where id = ?", (total_price, session["user_id"]))
                con.execute("insert into transactions (user_id, name, symbol, shares, price) values (?, ?, ?, ?, ?)",
                            (session["user_id"], share_data["name"], share_data["symbol"],
                             '-' + request.form.get("shares"), price_per_share))
                flash("Sold")
        except sqlite3.Error as e:
            print('Transaction failed.', e)

        con.close()
        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
