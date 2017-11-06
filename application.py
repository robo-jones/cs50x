from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    # get the necessary account info from the database
    positions = db.execute("SELECT symbol, shares, cost FROM positions WHERE user_id = :id", id=session["user_id"])
    user = db.execute("SELECT username, cash FROM users WHERE id = :id", id=session["user_id"])[0]

    totalStockValue = 0

    # get the current price for each position, calculate other necessary values, and add them to position, formatting prices as usd
    for position in positions:
        try:
            currentPrice = lookup(position["symbol"])["price"]
        except TypeError:
            return apology("Something went wrong on our end. Please try again")

        totalStockValue += (position["shares"] * currentPrice)
        position["currentPrice"] = usd(currentPrice)
        position["totalValue"] = usd(position["shares"] * currentPrice)
        position["gain"] = usd(position["shares"] * currentPrice - position["cost"])
        position["cost"] = usd(position["cost"])

    user["totalWorth"] = usd(user["cash"] + totalStockValue)
    user["totalStockValue"] = usd(totalStockValue)
    user["cash"] = usd(user["cash"])

    return render_template("index.html", user=user, positions=positions)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""

    if request.method == "GET":
        return render_template("buy.html")

    elif request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        totalCost = 0
        errors = []

        # ensure all necessary form values are filled in
        if symbol == "":
            errors.append("Please enter a stock ticker symbol to purchase")
        if shares == "":
            errors.append("Please enter the number of shares to purchase")

        # check whether the number of shares entered is valid (this is a bit of a dirty hack utilizing exception processing to ensure the string can be properly cast to an integer value)
        if shares != "":
            try:
                shares = int(shares)
                if shares < 1:
                    errors.append("Please enter a valid number of shares to purchase")
            except ValueError:
                errors.append("Shares to purchase must be a whole number")

        # ensure that the symbol provided is valid, and, if so, calculate the total cost of the transaction
        stockInfo = lookup(symbol)
        if stockInfo == None and symbol != "":
            errors.append("Couldn't find any stocks with symbol {}".format(symbol))
        else:
            totalCost = shares * stockInfo["price"]

        # check if user has enough cash to complete the transaction
        rows = db.execute("SELECT cash FROM users WHERE (id=:id)", id=session["user_id"])
        cash = rows[0]["cash"]
        if totalCost > cash:
            errors.append("Unable to complete transaction: The total cost of {} exceeds your available funds by {}".format(usd(totalCost), usd(totalCost - cash)))

        # check if any errors have ocurred, and flash them
        if len(errors) > 0:
            for error in errors:
                flash(error)
            return render_template("buy.html")

        # otherwise, execute the transaction, flash a success message, and return to the index
        else:
            totalCost = shares * stockInfo["price"]
            db.execute("INSERT INTO transactions(user_id, type, symbol, price, shares) VALUES (:id, 'BUY', :symbol, :price, :shares)", id=session["user_id"], symbol=stockInfo["symbol"], price=stockInfo["price"], shares=shares)
            db.execute("UPDATE users SET cash=(cash - :cost) WHERE (id=:id)", cost=totalCost, id=session["user_id"])

            # determine whether to create a new position or update an existing one
            rows = db.execute("SELECT id, shares, cost FROM positions WHERE (user_id=:id) AND (symbol=:symbol)", id=session["user_id"], symbol=stockInfo["symbol"])
            if len(rows) > 0:
                position = rows[0]

                # if there is an existing position, we need to calculate the new cost basis
                costBasis = (position["cost"] + totalCost) / (position["shares"] + shares)
                db.execute("UPDATE positions SET shares = (shares + :purchased), cost = :newCost WHERE id = :id", purchased=shares, newCost=costBasis, id=position["id"])
            else:
                db.execute("INSERT INTO positions(user_id, symbol, shares, cost) VALUES (:id, :symbol, :shares, :cost)", id=session["user_id"], symbol=stockInfo["symbol"], shares=shares, cost=totalCost)

            flash("Successfully purchased {} shares of {} for {}".format(shares, stockInfo["symbol"], usd(totalCost)))
            return redirect(url_for("index"))


@app.route("/history")
@login_required
def history():
    """Show history of transactions."""

    # query for and format transactions
    transactions = db.execute("SELECT type, symbol, date, price, shares FROM transactions WHERE user_id=:id ORDER BY date", id=session["user_id"])
    for transaction in transactions:
        # compute, format, and store the total amount of a transaction, formatting purchases as negative numbers, for aesthetic reasons
        if transaction["type"] == "BUY":
            transaction["amount"] = "-" + usd(transaction["price"] * transaction["shares"])
        else:
            transaction["amount"] = usd(transaction["price"] * transaction["shares"])

        transaction["price"] = usd(transaction["price"])

    return render_template("history.html", transactions=transactions)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "GET":
        return render_template("quote.html")

    elif request.method == "POST":
        symbol = request.form.get("symbol")
        if symbol == "":
            flash("Please enter a ticker symbol")
            return render_template("quote.html")

        stock = lookup(symbol)
        if stock == None:
            flash("No results for ticker symbol {}".format(symbol))
            return render_template("quote.html")
        else:
            return render_template("quoted.html", symbol=stock["symbol"], name=stock["name"], price=usd(stock["price"]))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        errors = []

        # check if username is valid. flash an error message if it isn't
        newUsername = request.form.get("username")
        if newUsername == "":
            errors.append("Please enter a username")
        else:
            rows = db.execute("SELECT * FROM users WHERE username=:name", name=newUsername)
            if len(rows) != 0:
                errors.append("Username is already in use, please try a different one")

        # check the provided passwords for any errors, and flash messages as appropriate
        newPassword = request.form.get("password")
        retypedPassword = request.form.get("retypedPassword")
        if newPassword == "":
            errors.append("Please enter a password")
        if retypedPassword == "":
            errors.append("Please re-type your password")
        if newPassword != retypedPassword:
            errors.append("Password and re-typed password must match")

        # if there were any issues, flash the error messages and redirect back to the registration page
        if len(errors) != 0:
            for error in errors:
                flash(error)
            return render_template("register.html")

        # otherwise, add the user to the database and log them in
        else:
            hashedPassword = pwd_context.hash(newPassword)
            newUserId = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=newUsername, hash=hashedPassword)
            session["user_id"] = newUserId

            # redirect to index page
            return redirect(url_for("index"))

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""

    if request.method == "GET":
        return render_template("sell.html")

    elif request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        totalCost = 0
        errors = []

        # ensure all necessary form values are filled in
        if symbol == "":
            errors.append("Please enter a stock ticker symbol to sell")
        if shares == "":
            errors.append("Please enter the number of shares to sell")

        # check whether the number of shares entered is valid (this is a bit of a dirty hack utilizing exception processing to ensure the string can be properly cast to an integer value)
        if shares != "":
            try:
                shares = int(shares)
                if shares < 1:
                    errors.append("Please enter a valid number of shares to sell")
            except ValueError:
                errors.append("Shares to sell must be a whole number")

        # if there are any errors at this point, continuing is pointless. Flash the errors and reload the page
        if len(errors) > 0:
            for error in errors:
                flash(error)
            return render_template("sell.html")

        # ensure that the symbol provided is valid, and, if so, calculate the total cost of the transaction
        stockInfo = lookup(symbol)
        if stockInfo == None:
            # if this is not a valid stock, then continuing is pointless
            errors.append("Couldn't find any stocks with symbol {}".format(symbol))
            for error in errors:
                flash(error)
            return render_template("sell.html")
        else:
            totalCost = shares * stockInfo["price"]

        # check if user is trying to sell more shares than they own (or, indeed if they own any at all)
        rows = db.execute("SELECT id, shares FROM positions WHERE user_id=:id AND symbol=:symbol", id=session["user_id"], symbol=stockInfo["symbol"])
        if len(rows) == 0:
            errors.append("You don't currently own any shares of {}".format(stockInfo["symbol"]))
        else:
            position = rows[0]
            if shares > position["shares"]:
                errors.append("Unable to complete transaction: you only own {} shares of {}".format(position["shares"], stockInfo["symbol"]))

        # check if any errors have ocurred, and flash them
        if len(errors) > 0:
            for error in errors:
                flash(error)
            return render_template("sell.html")

        # otherwise, execute the transaction, flash a success message, and return to the index
        else:
            db.execute("INSERT INTO transactions(user_id, type, symbol, price, shares) VALUES (:id, 'SELL', :symbol, :price, :shares)", id=session["user_id"], symbol=stockInfo["symbol"], price=stockInfo["price"], shares=shares)
            db.execute("UPDATE users SET cash=(cash + :cost) WHERE (id=:id)", cost=totalCost, id=session["user_id"])

            # if all shares of a position were sold, delete the position, otherwise update the number of shares owned
            if shares < position["shares"]:
                db.execute("UPDATE positions SET shares = (shares - :sold), cost = (cost - :proceeds) WHERE id = :id", sold=shares, proceeds=totalCost, id=position["id"])
            else:
                db.execute("DELETE FROM positions WHERE id=:id", id=position["id"])

            flash("Successfully sold {} shares of {} for {}".format(shares, stockInfo["symbol"], usd(totalCost)))
            return redirect(url_for("index"))

@app.route("/account")
@login_required
def account():
    user = db.execute("SELECT username, cash FROM users WHERE id=:id", id=session["user_id"])[0]

    return render_template("account.html", user=user)

@app.route("/password", methods=["POST"])
@login_required
def password():
    """change a user's password"""

    errors = []

    # check if entered values are valid. flash an error message if any aren't
    oldPassword = request.form.get("oldPassword")
    if oldPassword == "":
        errors.append("Please enter your old password")
    else:
        hash = db.execute("SELECT hash FROM users WHERE id=:id", id=session["user_id"])[0]["hash"]
        print(hash)
        if not pwd_context.verify(oldPassword, hash):
            errors.append("Your old password was incorrect, please try again")

    newPassword = request.form.get("newPassword")
    retypedPassword = request.form.get("retypedPassword")
    if newPassword == "":
        errors.append("Please enter a new password")
    if retypedPassword == "":
        errors.append("Please re-type your new password")
    if newPassword != retypedPassword:
        errors.append("New password and re-typed password must match")

    # if there were any issues, flash the error messages and redirect back to the registration page
    if len(errors) != 0:
        for error in errors:
            flash(error)
        return redirect(url_for("account"))

    # otherwise, update the user's password, flash a success message, and redirect to the account page
    else:
        hashedPassword = pwd_context.hash(newPassword)
        db.execute("UPDATE users SET hash=:hash WHERE id=:id", hash=hashedPassword, id=session["user_id"])
        flash("Password changed successfully")
        return redirect(url_for("account"))