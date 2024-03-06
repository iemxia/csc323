import web
from web import form
import crypto

render = web.template.render("templates/")
urls = ("/", "index", "/users", "users", "/submit", "submit")

admin_key, admin_pkey = crypto.gen_keys()
bob_key, bob_pkey = crypto.gen_keys()


class index:
    def GET(self):
        raise web.seeother("/submit")


class users:
    def GET(self):
        return render.users(
            ("Admin", str(admin_pkey)),
            ("Bob", str(bob_pkey)),
            str(crypto.curve),
            str(crypto.base_point),
            str(crypto.bp_order),
        )


class submit:
    myform = form.Form(
        form.Textbox("recipient", form.notnull, description="Message recipient"),
        form.Textbox("message", form.notnull, description="Message"),
        form.Textbox("hmac", form.notnull, description="HMAC"),
        form.Textbox("pkey_x", form.notnull, description="Your public key X coordinate"),
        form.Textbox("pkey_y", form.notnull, description="Your public key Y coordinate"),
        form.Button("Submit", description="Submit"),
    )

    def GET(self):
        return render.generic(self.myform(), "Enter your message here", "", "", False)

    def POST(self):
        if not self.myform.validates():
            return render.generic(self.myform(), "", "", "Invalid form data.", False)
        try:
            msg, hmac = user_msg(
                self.myform.d.recipient.strip(),
                self.myform.d.message,
                self.myform.d.hmac.strip(),
                self.myform.d.pkey_x.strip(),
                self.myform.d.pkey_y.strip(),
            )
            return render.generic(self.myform(), msg, hmac, "", False)
        except ValueError as e:
            return render.generic(self.myform(), "", "", e, False)


def user_msg(username, msg, given_hmac, pub_key_x, pub_key_y):
    pub_key = crypto.EccAlgPoint(curve=crypto.curve, x=int(pub_key_x), y=int(pub_key_y))

    match username:
        case "Admin":
            s_key = admin_key
        case "Bob":
            s_key = bob_key
        case _:
            raise ValueError("Did not find a matching recipient")

    if crypto.verify_msg(msg, given_hmac, pub_key, s_key):
        if username == "Admin":
            reply = "What do you want?"
        elif username == "Bob" and pub_key == admin_pkey:
            reply = f"Hi admin! Here's my password: {bob_key}"
        else:
            reply = "Bob says hi!"
    else:
        reply = (
            "Huh, it looks like your hmac does not match your public key. "
            + "Would you like to double check that?"
        )
    # Our calculated hmac
    hmac = crypto.calculate_hmac(reply, crypto.get_shared_key(pub_key, s_key)).hexdigest()
    return (reply, hmac)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
