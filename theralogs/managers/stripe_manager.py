from decouple import config
import stripe


class stripe_manager:
    stripe_api_key = config("STRIPE_SECRET")
    cost_per_minute = 9  # Should be 9 for prod

    @classmethod
    def register_customer(cls, email):
        stripe.api_key = cls.stripe_api_key
        stripe_customer = stripe.Customer.create(email=email)
        return stripe_customer["id"]

    @classmethod
    def create_payment_method(cls, therapist, card_dict):
        stripe.api_key = cls.stripe_api_key
        if therapist.stripe_payment_method_id:
            try:  # Remove previous payment
                stripe.PaymentMethod.detach(
                    therapist.stripe_payment_method_id,
                )
            except:
                # TODO: Figure out how to handle this if you need to.
                pass
        try:  # Try to create new payment method
            stripe_payment_method = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": card_dict["number"],
                    "exp_month": card_dict["exp_month"],
                    "exp_year": card_dict["exp_year"],
                    "cvc": card_dict["cvc"],
                },
            )
        except:
            return False

        therapist.stripe_payment_method_id = stripe_payment_method["id"]
        try:  # Try to attach new payment method with stripe customer
            stripe.PaymentMethod.attach(
                therapist.stripe_payment_method_id,
                customer=therapist.stripe_customer_id,
            )
        except:
            # TODO: Figure out how to handle this if you need to.
            pass

        try:  # Update customer default payment method
            stripe.Customer.modify(
                therapist.stripe_customer_id,
                invoice_settings={
                    "default_payment_method": therapist.stripe_payment_method_id
                },
            )
        except:
            # TODO: Figure out how to handle this if you need to.
            pass
        therapist.save()
        return therapist.stripe_payment_method_id is not None

    @classmethod
    def charge_customer(cls, recording_time, patient):
        total_charge = int(recording_time * cls.cost_per_minute)
        stripe.api_key = cls.stripe_api_key
        try:
            charge = stripe.PaymentIntent.create(
                amount=total_charge,
                currency="usd",
                customer=patient.therapist.stripe_customer_id,
                payment_method=patient.therapist.stripe_payment_method_id,
                off_session=True,
                confirm=True,
            )
        except:
            return None
        return charge["id"]

    @classmethod
    def refund_charge_session(cls, refund_id):
        stripe.api_key = cls.stripe_api_key
        try:
            response = stripe.Refund.create(payment_intent=refund_id)
        except:
            return None
        if response["status"] == "succeeded":
            return True
        else:
            return False
