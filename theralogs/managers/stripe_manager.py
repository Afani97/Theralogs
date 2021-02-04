from decouple import config
import stripe


class stripe_manager:
    stripe_api_key = config("STRIPE_SECRET")
    cost_per_minute = 190  # Should be 19 for prod

    @classmethod
    def register_customer(cls, email):
        stripe.api_key = cls.stripe_api_key
        stripe_customer = stripe.Customer.create(email=email)
        return stripe_customer["id"]

    @classmethod
    def create_payment_method(cls, therapist, card_dict):
        stripe.api_key = cls.stripe_api_key
        stripe_payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": card_dict["number"],
                "exp_month": card_dict["exp_month"],
                "exp_year": card_dict["exp_year"],
                "cvc": card_dict["cvc"],
            },
        )
        if therapist.stripe_payment_method_id:
            stripe.PaymentMethod.detach(
                therapist.stripe_payment_method_id,
            )

        therapist.stripe_payment_method_id = stripe_payment_method["id"]
        stripe.PaymentMethod.attach(
            therapist.stripe_payment_method_id,
            customer=therapist.stripe_customer_id,
        )
        stripe.Customer.modify(
            therapist.stripe_customer_id,
            invoice_settings={
                "default_payment_method": therapist.stripe_payment_method_id
            },
        )
        therapist.save()

    @classmethod
    def charge_customer(cls, recording_time, patient):
        total_charge = int(recording_time * cls.cost_per_minute)
        stripe.api_key = cls.stripe_api_key
        stripe.PaymentIntent.create(
            amount=total_charge,
            currency="usd",
            customer=patient.therapist.stripe_customer_id,
            payment_method=patient.therapist.stripe_payment_method_id,
            off_session=True,
            confirm=True,
        )