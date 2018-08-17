from django.conf.urls import url

from . import views

app_name='fcards'

urlpatterns = [

    url(r"^start_session_latest/$",views.start_session_latest,name="start_session_latest"),
    url(r"^start_session_prev/$",views.start_session_prev,name="start_session_prev"),
    url(r"^start_session_randold/$",views.start_session_randold,name="start_session_randold"),
    url(r"^start_session_all/$",views.start_session_all,name="start_session_all"),
    url(r"^start_session_dated/(?P<index>[0-9]+)/", views.start_session_dated, name="start_session_dated"),
    url(r"^roll_back/$",views.roll_back,name="roll_back"),
    url(r"^roll_forward/$",views.roll_forward,name="roll_forward"),
    url(r"^user_guessing/$",views.UserGuessing.as_view(),name="user_guessing"),
    url(r"^awaiting_approval/$",views.AwaitingApproval.as_view(),name="awaiting_approval"),
    url(r"^approve_btn/$", views.ApproveButtonOnClick.as_view(), name="approve_btn_on_click"),
    url(r"^dont_approve_btn/$", views.DontApproveButtonOnClick.as_view (), name="dont_approve_btn_on_click"),
    url(r"^edit_btn/$", views.edit_btn_on_click, name="edit_btn_on_click"),
    url(r"^end_of_session/$", views.end_of_session, name="end_of_session"),
]
