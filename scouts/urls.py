from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.index,
        name="index"
    ),

    path(
        "login/",
        views.login,
        name="login"
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "register/scout/",
        views.scout_register,
        name="scout_register"
    ),

    path(
        "register/academy/",
        views.academy_register,
        name="academy_register"
    ),

    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "admin/pending-users/",
        views.pending_users,
        name="pending_users"
    ),

    path(
        "admin/approve-user/<int:user_id>/",
        views.approve_user,
        name="approve_user"
    ),

    path(
        "admin/reject-user/<int:user_id>/",
        views.reject_user,
        name="reject_user"
    ),

    path(
        "admin/view-academies/",
        views.view_academies,
        name="view_academies"
    ),

    path(
        "admin/academy/<int:academy_id>/players/",
        views.academy_players,
        name="academy_players"
    ),

    path(
        "admin/delete-academy/<int:academy_id>/",
        views.delete_academy,
        name="delete_academy"
    ),

    path(
        "admin/view-scouts/",
        views.view_scouts,
        name="view_scouts"
    ),

    path(
        "admin/delete-scout/<int:scout_id>/",
        views.delete_scout,
        name="delete_scout"
    ),

    path(
        "admin/view-certificate/<int:profile_id>/",
        views.view_certificate,
        name="view_certificate"
    ),

    path(
        "academy-dashboard/",
        views.academy_dashboard,
        name="academy_dashboard"
    ),

    path(
        "academy/add-player/",
        views.add_player,
        name="add_player"
    ),

    path(
        "academy/add-unevaluated-player/",
        views.add_unevaluated_player,
        name="add_unevaluated_player"
    ),

    path(
        "academy/unevaluated-players/",
        views.unevaluated_players,
        name="unevaluated_players"
    ),

    path(
        "academy/manage-players/",
        views.manage_players,
        name="manage_players"
    ),

    path(
        "academy/update-player/<int:player_id>/",
        views.update_player,
        name="update_player"
    ),

    path(
        "academy/delete-player/<int:player_id>/",
        views.delete_player,
        name="delete_player"
    ),

    path(
        "scout-dashboard/",
        views.scout_dashboard,
        name="scout_dashboard"
    ),

    path(
        "scout/academies/",
        views.academy_lists,
        name="academy_lists"
    ),

    path(
        "scout/player/<int:player_id>/",
        views.player_detail,
        name="player_detail"
    ),

    path(
        "scout/shortlist/<int:player_id>/",
        views.shortlist_player,
        name="shortlist_player"
    ),

    path(
        "scout/search/",
        views.search_players,
        name="search_players"
    ),

    path(
        "scout/remove-shortlist/<int:player_id>/",
        views.remove_from_shortlist,
        name="remove_from_shortlist"
    ),

    path(
        "scout/shortlisted/",
        views.shortlisted_players,
        name="shortlisted_players"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),
]