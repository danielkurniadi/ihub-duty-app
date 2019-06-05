from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)


class UserManager(BaseUserManager):
    """Manager class for reliable users management methods
    """
    def _create_user(self, email, password, matric, is_staff, is_superuser, **extra_fields):
        """Create active with speciied permission level
        """
        if not email:
            raise ValueError("Users must have an email address to sign up")
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            matric=matric,
            is_staff=is_staff,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password, matric, **extra_fields):
        """Create basic permission level user
        """
        return self._create_user(email, password, matric, False, False, **extra_fields)

    def create_superuser(self, email, password, matric, **extra_fields):
        """Create superuser with high permission level
        """
        user = self._create_user(email, password, matric, True, True, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=254, blank=False)
    matric = models.CharField(max_length=9, unique=True, blank=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return '/users/%i/' % (self.pk)

    def __str__(self):
        return "User of %s - %s" % (self.name, self.email)

    def __eq__(self, other):
        if isinstance(other, User):
            return (self.email == other.email) and (self.matric = other.matric)
        return False
