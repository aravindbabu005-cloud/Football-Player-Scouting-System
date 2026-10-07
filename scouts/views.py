from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.views.decorators.cache import never_cache
import re

from .models import (
    UserProfile,
    Academy,
    Player,
    ShortlistedPlayer
)


# Home page
def index(request):

    return render(
        request,
        "index.html"
    )


# Set login session
def set_login_session(request, user, role):

    request.session.cycle_key()

    request.session["username"] = user.username
    request.session["user_role"] = role
    request.session["login_time"] = timezone.now().isoformat()

    request.session["admin_logged_in"] = role == "admin"
    request.session["scout_logged_in"] = role == "scout"
    request.session["academy_logged_in"] = role == "academy"

    request.session.set_expiry(1800)
    request.session.modified = True


# Validate username
def validate_username(username):

    if not username:
        return "Username is required."

    if len(username) < 3:
        return "Username must contain at least 3 characters."

    if len(username) > 150:
        return "Username must not exceed 150 characters."

    if not re.match(
        r"^[A-Za-z0-9_]+$",
        username
    ):
        return "Username can contain only letters, numbers and underscore."

    return None


# Validate email
def validate_user_email(email):

    if not email:
        return "Email is required."

    try:

        validate_email(email)

    except ValidationError:

        return "Please enter a valid email address."

    return None


# Validate password
def validate_password(password, confirm_password):

    if not password:
        return "Password is required."

    if len(password) < 8:
        return "Password must contain at least 8 characters."

    if not any(
        character.isupper()
        for character in password
    ):
        return "Password must contain at least one uppercase letter."

    if not any(
        character.islower()
        for character in password
    ):
        return "Password must contain at least one lowercase letter."

    if not any(
        character.isdigit()
        for character in password
    ):
        return "Password must contain at least one number."

    if password != confirm_password:
        return "Passwords do not match."

    return None


# Validate certificate
def validate_certificate(certificate):

    if not certificate:
        return "Certificate is required."

    allowed_extensions = [
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png"
    ]

    certificate_name = certificate.name.lower()

    if not any(
        certificate_name.endswith(extension)
        for extension in allowed_extensions
    ):
        return "Certificate must be PDF, JPG, JPEG or PNG."

    if certificate.size > 5 * 1024 * 1024:
        return "Certificate size must be below 5 MB."

    return None


# Login
@never_cache
def login(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        if not username or not password:

            messages.error(
                request,
                "Username and password are required."
            )

            return render(
                request,
                "login.html"
            )

        login_username = username

        academy = Academy.objects.filter(
            name__iexact=username
        ).select_related(
            "user"
        ).first()

        if academy:
            login_username = academy.user.username

        user = authenticate(
            request,
            username=login_username,
            password=password
        )

        if user is None:

            messages.error(
                request,
                "Invalid username or password."
            )

            return render(
                request,
                "login.html"
            )

        if user.is_superuser:

            auth_login(
                request,
                user
            )

            set_login_session(
                request,
                user,
                "admin"
            )

            return redirect(
                "admin_dashboard"
            )

        try:

            profile = UserProfile.objects.get(
                user=user
            )

        except UserProfile.DoesNotExist:

            messages.error(
                request,
                "User profile not found."
            )

            return render(
                request,
                "login.html"
            )

        if profile.role not in [
            "scout",
            "academy"
        ]:

            messages.error(
                request,
                "Invalid user role."
            )

            return render(
                request,
                "login.html"
            )

        if not profile.is_approved:

            messages.warning(
                request,
                "Your account is waiting for admin approval."
            )

            return redirect(
                "login"
            )

        if profile.role == "academy":

            academy = Academy.objects.filter(
                user=user
            ).first()

            if not academy:

                messages.error(
                    request,
                    "Academy profile not found."
                )

                return render(
                    request,
                    "login.html"
                )

            if not academy.is_approved:

                messages.warning(
                    request,
                    "Your academy account is waiting for admin approval."
                )

                return redirect(
                    "login"
                )

        auth_login(
            request,
            user
        )

        set_login_session(
            request,
            user,
            profile.role
        )

        if profile.role == "scout":

            return redirect(
                "scout_dashboard"
            )

        if profile.role == "academy":

            return redirect(
                "academy_dashboard"
            )

        logout(request)

        request.session.flush()

        messages.error(
            request,
            "Invalid user role."
        )

        return redirect(
            "login"
        )

    return render(
        request,
        "login.html"
    )


# Registration role selection
def register(request):

    if request.method == "POST":

        role = request.POST.get(
            "role",
            ""
        ).strip().lower()

        if role == "scout":

            return redirect(
                "scout_register"
            )

        if role == "academy":

            return redirect(
                "academy_register"
            )

        messages.error(
            request,
            "Please select a valid registration type."
        )

    return render(
        request,
        "register.html"
    )


# Scout registration
def scout_register(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        current_club = request.POST.get(
            "current_club",
            ""
        ).strip()

        certificate = request.FILES.get(
            "certificate"
        )

        username_error = validate_username(
            username
        )

        if username_error:

            messages.error(
                request,
                username_error
            )

            return render(
                request,
                "scout_register.html"
            )

        email_error = validate_user_email(
            email
        )

        if email_error:

            messages.error(
                request,
                email_error
            )

            return render(
                request,
                "scout_register.html"
            )

        password_error = validate_password(
            password,
            confirm_password
        )

        if password_error:

            messages.error(
                request,
                password_error
            )

            return render(
                request,
                "scout_register.html"
            )

        if not current_club:

            messages.error(
                request,
                "Current club is required."
            )

            return render(
                request,
                "scout_register.html"
            )

        if len(current_club) < 2:

            messages.error(
                request,
                "Current club name is too short."
            )

            return render(
                request,
                "scout_register.html"
            )

        if User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return render(
                request,
                "scout_register.html"
            )

        if User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return render(
                request,
                "scout_register.html"
            )

        certificate_error = validate_certificate(
            certificate
        )

        if certificate_error:

            messages.error(
                request,
                certificate_error
            )

            return render(
                request,
                "scout_register.html"
            )

        try:

            with transaction.atomic():

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                UserProfile.objects.create(
                    user=user,
                    role="scout",
                    current_club=current_club,
                    certificate=certificate,
                    is_approved=False
                )

            send_mail(
                "Scout Registration Received",
                f"""
Hello {username},

Your scout registration has been received successfully.

Your account is currently waiting for admin approval.

You will receive another email once your account is approved.

Regards,
Player Scouting System
""",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True
            )

            messages.success(
                request,
                "Registration successful. Your account is waiting for admin approval."
            )

            return redirect(
                "login"
            )

        except IntegrityError:

            messages.error(
                request,
                "Registration failed. Please try again."
            )

    return render(
        request,
        "scout_register.html"
    )


# Academy registration
def academy_register(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        academy_name = request.POST.get(
            "academy_name",
            ""
        ).strip()

        location = request.POST.get(
            "location",
            ""
        ).strip()

        certificate = request.FILES.get(
            "certificate"
        )

        username_error = validate_username(
            username
        )

        if username_error:

            messages.error(
                request,
                username_error
            )

            return render(
                request,
                "academy_register.html"
            )

        email_error = validate_user_email(
            email
        )

        if email_error:

            messages.error(
                request,
                email_error
            )

            return render(
                request,
                "academy_register.html"
            )

        password_error = validate_password(
            password,
            confirm_password
        )

        if password_error:

            messages.error(
                request,
                password_error
            )

            return render(
                request,
                "academy_register.html"
            )

        if not academy_name:

            messages.error(
                request,
                "Academy name is required."
            )

            return render(
                request,
                "academy_register.html"
            )

        if len(academy_name) < 2:

            messages.error(
                request,
                "Academy name is too short."
            )

            return render(
                request,
                "academy_register.html"
            )

        if not location:

            messages.error(
                request,
                "Location is required."
            )

            return render(
                request,
                "academy_register.html"
            )

        if len(location) < 2:

            messages.error(
                request,
                "Location is too short."
            )

            return render(
                request,
                "academy_register.html"
            )

        if User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return render(
                request,
                "academy_register.html"
            )

        if User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return render(
                request,
                "academy_register.html"
            )

        if Academy.objects.filter(
            name__iexact=academy_name
        ).exists():

            messages.error(
                request,
                "Academy name already exists."
            )

            return render(
                request,
                "academy_register.html"
            )

        certificate_error = validate_certificate(
            certificate
        )

        if certificate_error:

            messages.error(
                request,
                certificate_error
            )

            return render(
                request,
                "academy_register.html"
            )

        try:

            with transaction.atomic():

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                UserProfile.objects.create(
                    user=user,
                    role="academy",
                    certificate=certificate,
                    is_approved=False
                )

                Academy.objects.create(
                    user=user,
                    name=academy_name,
                    location=location,
                    is_approved=False
                )

            send_mail(
                "Academy Registration Received",
                f"""
Hello {academy_name},

Your academy registration has been received successfully.

Your account is currently waiting for admin approval.

You will receive another email once your account is approved.

Regards,
Player Scouting System
""",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True
            )

            messages.success(
                request,
                "Registration successful. Your account is waiting for admin approval."
            )

            return redirect(
                "login"
            )

        except IntegrityError:

            messages.error(
                request,
                "Registration failed. Please try again."
            )

    return render(
        request,
        "academy_register.html"
    )


# Admin access
def admin_required(request):

    if not request.user.is_authenticated:
        return False

    if not request.user.is_superuser:
        return False

    if request.session.get(
        "user_role"
    ) != "admin":
        return False

    if not request.session.get(
        "admin_logged_in"
    ):
        return False

    return True


# Admin dashboard
@never_cache
def admin_dashboard(request):

    if not admin_required(request):

        return redirect(
            "login"
        )

    academy_count = Academy.objects.filter(
        is_approved=True
    ).count()

    scout_count = UserProfile.objects.filter(
        role="scout",
        is_approved=True
    ).count()

    pending_count = UserProfile.objects.filter(
        is_approved=False
    ).count()

    return render(
        request,
        "admin_dashboard.html",
        {
            "academy_count": academy_count,
            "scout_count": scout_count,
            "pending_count": pending_count
        }
    )


# Pending users
@never_cache
def pending_users(request):

    if not admin_required(request):

        return redirect(
            "login"
        )

    pending_profiles = UserProfile.objects.filter(
        is_approved=False
    ).select_related(
        "user"
    )

    return render(
        request,
        "admin/pending_users.html",
        {
            "pending_profiles": pending_profiles
        }
    )


# Approve user
@never_cache
def approve_user(request, user_id):

    if not admin_required(request):

        return redirect(
            "login"
        )

    user = get_object_or_404(
        User,
        id=user_id
    )

    profile = get_object_or_404(
        UserProfile,
        user=user
    )

    profile.is_approved = True
    profile.save()

    if profile.role == "academy":

        academy = Academy.objects.filter(
            user=user
        ).first()

        if academy:

            academy.is_approved = True
            academy.save()

    send_mail(
        "Account Approved",
        f"""
Hello {user.username},

Your Player Scouting System account has been approved by the administrator.

You can now log in to your account.

Regards,
Player Scouting System
""",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True
    )

    messages.success(
        request,
        f"{user.username} has been approved successfully."
    )

    return redirect(
        "pending_users"
    )


# Reject user
@never_cache
def reject_user(request, user_id):

    if not admin_required(request):

        return redirect(
            "login"
        )

    user = get_object_or_404(
        User,
        id=user_id
    )

    username = user.username

    user.delete()

    messages.success(
        request,
        f"{username} has been rejected."
    )

    return redirect(
        "pending_users"
    )


# View academies
@never_cache
def view_academies(request):

    if not admin_required(request):

        return redirect(
            "login"
        )

    academies = Academy.objects.filter(
        is_approved=True
    ).select_related(
        "user"
    )

    return render(
        request,
        "admin/view_academies.html",
        {
            "academies": academies
        }
    )


# View academy players
@never_cache
def academy_players(request, academy_id):

    if not admin_required(request):

        return redirect(
            "login"
        )

    academy = get_object_or_404(
        Academy,
        id=academy_id
    )

    players = Player.objects.filter(
        academy=academy
    )

    return render(
        request,
        "admin/academy_players.html",
        {
            "academy": academy,
            "players": players
        }
    )


# Delete academy
@never_cache
def delete_academy(request, academy_id):

    if not admin_required(request):

        return redirect(
            "login"
        )

    academy = get_object_or_404(
        Academy,
        id=academy_id
    )

    user = academy.user

    academy.delete()

    if user:
        user.delete()

    messages.success(
        request,
        "Academy deleted successfully."
    )

    return redirect(
        "view_academies"
    )


# View scouts
@never_cache
def view_scouts(request):

    if not admin_required(request):

        return redirect(
            "login"
        )

    scouts = UserProfile.objects.filter(
        role="scout",
        is_approved=True
    ).select_related(
        "user"
    )

    return render(
        request,
        "admin/view_scouts.html",
        {
            "scouts": scouts
        }
    )


# Delete scout
@never_cache
def delete_scout(request, scout_id):

    if not admin_required(request):

        return redirect(
            "login"
        )

    profile = get_object_or_404(
        UserProfile,
        id=scout_id,
        role="scout"
    )

    user = profile.user

    profile.delete()

    if user:
        user.delete()

    messages.success(
        request,
        "Scout deleted successfully."
    )

    return redirect(
        "view_scouts"
    )


# View certificate
@never_cache
def view_certificate(request, profile_id):

    if not admin_required(request):

        return redirect(
            "login"
        )

    profile = get_object_or_404(
        UserProfile,
        id=profile_id
    )

    if not profile.certificate:

        messages.error(
            request,
            "Certificate not found."
        )

        return redirect(
            "pending_users"
        )

    return render(
        request,
        "admin/view_certificate.html",
        {
            "profile": profile
        }
    )


# Get approved profile
def get_approved_profile(request, role):

    if not request.user.is_authenticated:
        return None

    if request.session.get(
        "user_role"
    ) != role:
        return None

    if role == "scout":

        if not request.session.get(
            "scout_logged_in"
        ):
            return None

    if role == "academy":

        if not request.session.get(
            "academy_logged_in"
        ):
            return None

    try:

        profile = UserProfile.objects.get(
            user=request.user,
            role=role,
            is_approved=True
        )

    except UserProfile.DoesNotExist:

        return None

    if role == "academy":

        academy = Academy.objects.filter(
            user=request.user,
            is_approved=True
        ).first()

        if not academy:
            return None

    return profile


# Academy dashboard
@never_cache
def academy_dashboard(request):

    profile = get_approved_profile(
        request,
        "academy"
    )

    if not profile:

        return redirect(
            "login"
        )

    academy = Academy.objects.filter(
        user=request.user,
        is_approved=True
    ).first()

    if not academy:

        return redirect(
            "login"
        )

    player_count = Player.objects.filter(
        academy=academy
    ).count()

    unevaluated_count = Player.objects.filter(
        academy=academy,
        is_evaluated=False
    ).count()

    return render(
        request,
        "academy_dashboard.html",
        {
            "profile": profile,
            "academy": academy,
            "player_count": player_count,
            "unevaluated_count": unevaluated_count
        }
    )


# Add player
@never_cache
def add_player(request):

    profile = get_approved_profile(
        request,
        "academy"
    )

    if not profile:

        return redirect(
            "login"
        )

    academy = get_object_or_404(
        Academy,
        user=request.user,
        is_approved=True
    )

    if request.method == "POST":

        Player.objects.create(
            academy=academy,

            name=request.POST.get(
                "name",
                ""
            ).strip(),

            age=request.POST.get(
                "age"
            ) or 0,

            position=request.POST.get(
                "position",
                ""
            ).strip(),

            preferred_foot=request.POST.get(
                "preferred_foot",
                ""
            ).strip(),

            height=request.POST.get(
                "height"
            ) or 0,

            weight=request.POST.get(
                "weight"
            ) or 0,

            phone=request.POST.get(
                "phone",
                ""
            ).strip(),

            photo=request.FILES.get(
                "photo"
            ),

            speed=request.POST.get(
                "speed"
            ) or 0,

            shooting=request.POST.get(
                "shooting"
            ) or 0,

            passing=request.POST.get(
                "passing"
            ) or 0,

            dribbling=request.POST.get(
                "dribbling"
            ) or 0,

            ball_control=request.POST.get(
                "ball_control"
            ) or 0,

            crossing=request.POST.get(
                "crossing"
            ) or 0,

            finishing=request.POST.get(
                "finishing"
            ) or 0,

            heading=request.POST.get(
                "heading"
            ) or 0,

            acceleration=request.POST.get(
                "acceleration"
            ) or 0,

            agility=request.POST.get(
                "agility"
            ) or 0,

            balance=request.POST.get(
                "balance"
            ) or 0,

            stamina=request.POST.get(
                "stamina"
            ) or 0,

            strength=request.POST.get(
                "strength"
            ) or 0,

            jumping=request.POST.get(
                "jumping"
            ) or 0,

            defending=request.POST.get(
                "defending"
            ) or 0,

            tackling=request.POST.get(
                "tackling"
            ) or 0,

            interceptions=request.POST.get(
                "interceptions"
            ) or 0,

            marking=request.POST.get(
                "marking"
            ) or 0,

            vision=request.POST.get(
                "vision"
            ) or 0,

            decision_making=request.POST.get(
                "decision_making"
            ) or 0,

            positioning=request.POST.get(
                "positioning"
            ) or 0,

            composure=request.POST.get(
                "composure"
            ) or 0,

            is_evaluated=True
        )

        messages.success(
            request,
            "Player added successfully."
        )

        return redirect(
            "manage_players"
        )

    return render(
        request,
        "academy/add_player.html",
        {
            "profile": profile,
            "academy": academy
        }
    )


# Add unevaluated player
@never_cache
def add_unevaluated_player(request):

    profile = get_approved_profile(
        request,
        "academy"
    )

    if not profile:

        return redirect(
            "login"
        )

    academy = get_object_or_404(
        Academy,
        user=request.user,
        is_approved=True
    )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        age = request.POST.get(
            "age"
        ) or 0

        position = request.POST.get(
            "position",
            ""
        ).strip()

        if not name:

            messages.error(
                request,
                "Player name is required."
            )

            return render(
                request,
                "academy/add_unevaluated_player.html",
                {
                    "profile": profile,
                    "academy": academy
                }
            )

        if not position:

            messages.error(
                request,
                "Player position is required."
            )

            return render(
                request,
                "academy/add_unevaluated_player.html",
                {
                    "profile": profile,
                    "academy": academy
                }
            )

        Player.objects.create(
            academy=academy,
            name=name,
            age=age,
            position=position,
            is_evaluated=False
        )

        messages.success(
            request,
            "Unevaluated player added successfully."
        )

        return redirect(
            "unevaluated_players"
        )

    return render(
        request,
        "academy/add_unevaluated_player.html",
        {
            "profile": profile,
            "academy": academy
        }
    )


# Unevaluated players
@never_cache
def unevaluated_players(request):

    profile = get_approved_profile(
        request,
        "academy"
    )

    if not profile:

        return redirect(
            "login"
        )

    academy = get_object_or_404(
        Academy,
        user=request.user,
        is_approved=True
    )

    players = Player.objects.filter(
        academy=academy,
        is_evaluated=False
    )

    return render(
        request,
        "academy/unevaluated_players.html",
        {
            "profile": profile,
            "academy": academy,
            "players": players
        }
    )


# Manage players
@never_cache
def manage_players(request):

    profile = get_approved_profile(
        request,
        "academy"
    )

    if not profile:

        return redirect(
            "login"
        )

    academy = get_object_or_404(
        Academy,
        user=request.user,
        is_approved=True
    )

    players = Player.objects.filter(
        academy=academy
    )

    return render(
        request,
        "academy/manage_players.html",
        {
            "profile": profile,
            "academy": academy,
            "players": players
        }
    )


# Update player
@never_cache
def update_player(request, player_id):

    profile = get_approved_profile(
        request,
        "academy"
    )

    if not profile:

        return redirect(
            "login"
        )

    academy = get_object_or_404(
        Academy,
        user=request.user,
        is_approved=True
    )

    player = get_object_or_404(
        Player,
        id=player_id,
        academy=academy
    )

    if request.method == "POST":

        player.name = request.POST.get(
            "name",
            ""
        ).strip()

        player.age = request.POST.get(
            "age"
        ) or 0

        player.position = request.POST.get(
            "position",
            ""
        ).strip()

        player.preferred_foot = request.POST.get(
            "preferred_foot",
            ""
        ).strip()

        player.height = request.POST.get(
            "height"
        ) or 0

        player.weight = request.POST.get(
            "weight"
        ) or 0

        player.phone = request.POST.get(
            "phone",
            ""
        ).strip()

        if request.FILES.get("photo"):

            player.photo = request.FILES.get(
                "photo"
            )

        player.speed = request.POST.get(
            "speed"
        ) or 0

        player.shooting = request.POST.get(
            "shooting"
        ) or 0

        player.passing = request.POST.get(
            "passing"
        ) or 0

        player.dribbling = request.POST.get(
            "dribbling"
        ) or 0

        player.ball_control = request.POST.get(
            "ball_control"
        ) or 0

        player.crossing = request.POST.get(
            "crossing"
        ) or 0

        player.finishing = request.POST.get(
            "finishing"
        ) or 0

        player.heading = request.POST.get(
            "heading"
        ) or 0

        player.acceleration = request.POST.get(
            "acceleration"
        ) or 0

        player.agility = request.POST.get(
            "agility"
        ) or 0

        player.balance = request.POST.get(
            "balance"
        ) or 0

        player.stamina = request.POST.get(
            "stamina"
        ) or 0

        player.strength = request.POST.get(
            "strength"
        ) or 0

        player.jumping = request.POST.get(
            "jumping"
        ) or 0

        player.defending = request.POST.get(
            "defending"
        ) or 0

        player.tackling = request.POST.get(
            "tackling"
        ) or 0

        player.interceptions = request.POST.get(
            "interceptions"
        ) or 0

        player.marking = request.POST.get(
            "marking"
        ) or 0

        player.vision = request.POST.get(
            "vision"
        ) or 0

        player.decision_making = request.POST.get(
            "decision_making"
        ) or 0

        player.positioning = request.POST.get(
            "positioning"
        ) or 0

        player.composure = request.POST.get(
            "composure"
        ) or 0

        player.save()

        messages.success(
            request,
            "Player updated successfully."
        )

        return redirect(
            "manage_players"
        )

    return render(
        request,
        "academy/update_player.html",
        {
            "profile": profile,
            "academy": academy,
            "player": player
        }
    )


# Delete player
@never_cache
def delete_player(request, player_id):

    profile = get_approved_profile(
        request,
        "academy"
    )

    if not profile:

        return redirect(
            "login"
        )

    academy = get_object_or_404(
        Academy,
        user=request.user,
        is_approved=True
    )

    player = get_object_or_404(
        Player,
        id=player_id,
        academy=academy
    )

    player.delete()

    messages.success(
        request,
        "Player deleted successfully."
    )

    return redirect(
        "manage_players"
    )


# Scout dashboard
@never_cache
def scout_dashboard(request):

    profile = get_approved_profile(
        request,
        "scout"
    )

    if not profile:

        return redirect(
            "login"
        )

    shortlisted_count = ShortlistedPlayer.objects.filter(
        scout=request.user
    ).count()

    return render(
        request,
        "scout_dashboard.html",
        {
            "profile": profile,
            "shortlisted_count": shortlisted_count
        }
    )


# Academy list
@never_cache
def academy_lists(request):

    profile = get_approved_profile(
        request,
        "scout"
    )

    if not profile:

        return redirect(
            "login"
        )

    # Get all approved academies
    academies = Academy.objects.filter(
        is_approved=True
    )

    # Get the academy ID from the View Players button
    academy_id = request.GET.get(
        "academy_id",
        ""
    ).strip()

    selected_academy = None
    players = Player.objects.none()

    if academy_id:

        # Get only the selected approved academy
        selected_academy = get_object_or_404(
            Academy,
            id=academy_id,
            is_approved=True
        )

        # Get only players belonging to this academy
        players = Player.objects.filter(
            academy=selected_academy
        ).select_related(
            "academy"
        )

    # Get shortlisted player IDs for this scout
    shortlisted_ids = set(
        ShortlistedPlayer.objects.filter(
            scout=request.user
        ).values_list(
            "player_id",
            flat=True
        )
    )

    return render(
        request,
        "scout/academy_lists.html",
        {
            "profile": profile,
            "academies": academies,
            "selected_academy": selected_academy,
            "players": players,
            "shortlisted_ids": shortlisted_ids
        }
    )


# Player detail
@never_cache
def player_detail(request, player_id):

    profile = get_approved_profile(
        request,
        "scout"
    )

    if not profile:

        return redirect(
            "login"
        )

    player = get_object_or_404(
        Player.objects.select_related(
            "academy"
        ),
        id=player_id,
        academy__is_approved=True
    )

    is_shortlisted = ShortlistedPlayer.objects.filter(
        scout=request.user,
        player=player
    ).exists()

    return render(
        request,
        "scout/player_detail.html",
        {
            "profile": profile,
            "player": player,
            "is_shortlisted": is_shortlisted
        }
    )


# Shortlist player
@never_cache
def shortlist_player(request, player_id):

    profile = get_approved_profile(
        request,
        "scout"
    )

    if not profile:

        return redirect(
            "login"
        )

    player = get_object_or_404(
        Player,
        id=player_id,
        academy__is_approved=True
    )

    ShortlistedPlayer.objects.get_or_create(
        scout=request.user,
        player=player
    )

    messages.success(
        request,
        f"{player.name} has been shortlisted."
    )

    next_page = request.POST.get(
        "next"
    )

    if next_page:

        return redirect(
            next_page
        )

    return redirect(
        "scout_dashboard"
    )


# Search players
@never_cache
def search_players(request):

    profile = get_approved_profile(
        request,
        "scout"
    )

    if not profile:

        return redirect(
            "login"
        )

    search_fields = [
        "position",
        "age",
        "preferred_foot",
        "height",
        "weight",
        "speed",
        "shooting",
        "passing",
        "dribbling",
        "ball_control",
        "crossing",
        "finishing",
        "heading",
        "acceleration",
        "agility",
        "balance",
        "stamina",
        "strength",
        "jumping",
        "defending",
        "tackling",
        "interceptions",
        "marking",
        "vision",
        "decision_making",
        "positioning",
        "composure"
    ]

    values = {}

    for field in search_fields:

        values[field] = request.GET.get(
            field,
            ""
        ).strip()

    has_search = any(
        value != ""
        for value in values.values()
    )

    players = Player.objects.filter(
        academy__is_approved=True
    ).select_related(
        "academy"
    )

    shortlisted_ids = set(
        ShortlistedPlayer.objects.filter(
            scout=request.user
        ).values_list(
            "player_id",
            flat=True
        )
    )

    player_results = []

    if has_search:

        def to_float(value):

            try:

                return float(value)

            except (
                TypeError,
                ValueError
            ):

                return None

        def numeric_closeness(
            player_value,
            requested_value
        ):

            player_number = to_float(
                player_value
            )

            requested_number = to_float(
                requested_value
            )

            if (
                player_number is None
                or requested_number is None
            ):

                return 0

            if requested_number == 0:

                if player_number == 0:
                    return 100

                return 0

            difference = abs(
                player_number
                - requested_number
            )

            percentage = (
                100
                - (
                    difference
                    / abs(requested_number)
                    * 100
                )
            )

            return max(
                0,
                min(
                    percentage,
                    100
                )
            )

        def skill_match(
            player_value,
            requested_value
        ):

            player_number = to_float(
                player_value
            )

            requested_number = to_float(
                requested_value
            )

            if (
                player_number is None
                or requested_number is None
            ):

                return 0

            if requested_number <= 0:
                return 100

            percentage = (
                player_number
                / requested_number
                * 100
            )

            return max(
                0,
                min(
                    percentage,
                    100
                )
            )

        skill_fields = [
            "speed",
            "shooting",
            "passing",
            "dribbling",
            "ball_control",
            "crossing",
            "finishing",
            "heading",
            "acceleration",
            "agility",
            "balance",
            "stamina",
            "strength",
            "jumping",
            "defending",
            "tackling",
            "interceptions",
            "marking",
            "vision",
            "decision_making",
            "positioning",
            "composure"
        ]

        for player in players:

            scores = []

            if values["position"]:

                player_position = (
                    player.position or ""
                ).strip().lower()

                requested_position = (
                    values["position"]
                    .strip()
                    .lower()
                )

                if player_position == requested_position:
                    scores.append(100)

                else:
                    scores.append(0)

            if values["preferred_foot"]:

                player_foot = (
                    player.preferred_foot or ""
                ).strip().lower()

                requested_foot = (
                    values["preferred_foot"]
                    .strip()
                    .lower()
                )

                if player_foot == requested_foot:
                    scores.append(100)

                else:
                    scores.append(0)

            if values["age"]:

                scores.append(
                    numeric_closeness(
                        player.age,
                        values["age"]
                    )
                )

            if values["height"]:

                scores.append(
                    numeric_closeness(
                        player.height,
                        values["height"]
                    )
                )

            if values["weight"]:

                scores.append(
                    numeric_closeness(
                        player.weight,
                        values["weight"]
                    )
                )

            for field_name in skill_fields:

                requested_value = values[
                    field_name
                ]

                if requested_value:

                    player_value = getattr(
                        player,
                        field_name,
                        0
                    )

                    scores.append(
                        skill_match(
                            player_value,
                            requested_value
                        )
                    )

            if scores:

                match_percentage = round(
                    sum(scores)
                    / len(scores)
                )

            else:

                match_percentage = 0

            player_results.append(
                {
                    "player": player,
                    "match_percentage": match_percentage
                }
            )

        player_results.sort(
            key=lambda result: result[
                "match_percentage"
            ],
            reverse=True
        )

    context = {
        "profile": profile,
        "player_results": player_results,
        "shortlisted_ids": shortlisted_ids
    }

    context.update(
        values
    )

    return render(
        request,
        "scout/search_players.html",
        context
    )


# Remove player from shortlist
@never_cache
def remove_from_shortlist(request, player_id):

    profile = get_approved_profile(
        request,
        "scout"
    )

    if not profile:

        return redirect(
            "login"
        )

    shortlist = ShortlistedPlayer.objects.filter(
        scout=request.user,
        player_id=player_id
    )

    if shortlist.exists():

        shortlist.delete()

        messages.success(
            request,
            "Player removed from shortlist."
        )

    return redirect(
        request.POST.get(
            "next",
            "shortlisted_players"
        )
    )


# Shortlisted players
@never_cache
def shortlisted_players(request):

    profile = get_approved_profile(
        request,
        "scout"
    )

    if not profile:

        return redirect(
            "login"
        )

    shortlisted_players_list = (
        ShortlistedPlayer.objects.filter(
            scout=request.user,
            player__academy__is_approved=True
        )
        .select_related(
            "player",
            "player__academy"
        )
    )

    return render(
        request,
        "scout/shortlisted_players.html",
        {
            "profile": profile,
            "shortlisted_players": shortlisted_players_list
        }
    )


# Logout
@never_cache
def logout_view(request):

    logout(request)

    request.session.flush()

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect(
        "login"
    )