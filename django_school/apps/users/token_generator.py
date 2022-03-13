from django.contrib.auth.tokens import PasswordResetTokenGenerator


class SetPasswordTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        user.password = "" if user.password is None else user.password
        hash_value = super()._make_hash_value(user, timestamp)

        return f"{hash_value}{user.is_active}"


set_password_token_generator = SetPasswordTokenGenerator()
