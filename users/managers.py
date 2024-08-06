from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, bio=None, avatar=None):
        if not username:
            raise ValueError('User must have a username')
        if not email:
            raise ValueError('User must have a Email')

        user = self.model(username=username, email=self.normalize_email(email), bio=bio, avatar=avatar)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, bio=None, avatar=None):
        user = self.create_user(username, email, password, bio, avatar)
        user.is_admin = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user
