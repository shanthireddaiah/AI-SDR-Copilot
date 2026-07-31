import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

logger = logging.getLogger('accounts')

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that permits users to log in
    using either their username OR their email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if not username or not password:
            logger.warning("[AUTH] Authentication attempted with empty username or password.")
            return None

        # Look for user matching username OR email (case-insensitive)
        try:
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except UserModel.DoesNotExist:
            logger.warning(f"[AUTH FAIL] No user found with username/email: '{username}'")
            return None
        except UserModel.MultipleObjectsReturned:
            # If multiple users share the same email, fetch by exact username first or fallback to first
            user = UserModel.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()

        if user:
            # Verify password
            if user.check_password(password):
                if self.user_can_authenticate(user):
                    logger.info(f"[AUTH SUCCESS] User '{user.username}' successfully authenticated.")
                    return user
                else:
                    logger.warning(f"[AUTH FAIL] User '{user.username}' exists & password match, but user is INACTIVE (is_active=False).")
                    return None
            else:
                logger.warning(f"[AUTH FAIL] User '{user.username}' exists, but PASSWORD MISMATCH.")
                return None

        return None
