from django.conf.urls import url

from . import views

app_name='fcards'

urlpatterns = [

    url(r"^start_session_randold/$",views.start_session_randold,name="start_session_randold"),
    url(r"^start_session_all/$",views.start_session_all,name="start_session_all"),
    url(r"^start_session_dated/(?P<date>.+)/", views.start_session_dated, name="start_session_dated"),
    url(r"^start_session_intervalled/(?P<start>.+)/(?P<size>.+)", views.start_session_intervalled, name="start_session_intervalled"),
    url(r"^start_session_intervalled_random/(?P<start>.+)/(?P<size>.+)", views.start_session_intervalled_random, name="start_session_intervalled_random"),
    url(r"^roll_back/$",views.roll_back,name="roll_back"),
    url(r"^roll_forward/$",views.roll_forward,name="roll_forward"),
    url(r"^user_guessing/$",views.UserGuessing.as_view(),name="user_guessing"),
    url(r"^awaiting_approval/$",views.AwaitingApproval.as_view(),name="awaiting_approval"),
    url(r"^approve_btn/$", views.ApproveButtonOnClick.as_view(), name="approve_btn_on_click"),
    url(r"^dont_approve_btn/$", views.DontApproveButtonOnClick.as_view (), name="dont_approve_btn_on_click"),
    url(r"^edit_btn/$", views.edit_btn_on_click, name="edit_btn_on_click"),
    url(r"^end_of_session/$", views.end_of_session, name="end_of_session"),
    url(r"^restart_session/$", views.restart_session_in_other_mode, name="restart_session"),
    url(r"^resume_session/$", views.funnel, name="funnel"),
    url(r"^resume_session/$", views.resume_session, name="resume_session"),
    url(r"^end_session_done/$", views.end_session_done, name="end_session_done"),

]
