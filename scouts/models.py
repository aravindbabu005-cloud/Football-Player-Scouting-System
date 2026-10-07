from django.db import models
from django.contrib.auth.models import User


# User Profile

class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("scout", "Scout"),
        ("academy", "Academy"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True,
        null=True
    )

    # Current Club

    current_club = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    # Certificate

    certificate = models.FileField(
        upload_to="certificate/",
        blank=True,
        null=True
    )

    # Approval Status

    is_approved = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.user.username


# Academy

class Academy(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=150
    )

    location = models.CharField(
        max_length=150
    )

    # Approval Status

    is_approved = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.name


# Player

class Player(models.Model):

    academy = models.ForeignKey(
        Academy,
        on_delete=models.CASCADE,
        related_name="players"
    )

    # Evaluation Status

    is_evaluated = models.BooleanField(
        default=True
    )

    # Basic Details

    name = models.CharField(
        max_length=150
    )

    age = models.PositiveIntegerField()

    position = models.CharField(
        max_length=100
    )

    preferred_foot = models.CharField(
        max_length=20,
        choices=[
            ("Right", "Right"),
            ("Left", "Left"),
            ("Both", "Both"),
        ],
        blank=True,
        null=True
    )

    height = models.FloatField(
        null=True,
        blank=True
    )

    weight = models.FloatField(
        null=True,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    photo = models.ImageField(
        upload_to="players/",
        blank=True,
        null=True
    )

    # Existing Performance

    speed = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    shooting = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    passing = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    dribbling = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    # Technical

    ball_control = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    crossing = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    finishing = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    heading = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    # Physical

    acceleration = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    agility = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    balance = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    stamina = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    strength = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    jumping = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    # Defensive

    defending = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    tackling = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    interceptions = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    marking = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    # Mental and Tactical

    vision = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    decision_making = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    positioning = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    composure = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


# Shortlisted Player

class ShortlistedPlayer(models.Model):

    scout = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shortlisted_players"
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="shortlisted_by"
    )

    shortlisted_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("scout", "player")

    def __str__(self):
        return f"{self.scout.username} - {self.player.name}"