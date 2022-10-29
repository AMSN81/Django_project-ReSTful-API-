import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from Site_Project.models import Report, Projects
from Site_User.models import User
from Project1.settings import ADMIN_BOT

# run python manage.py qcluster
def notif_admin():
    p_reports = Report.objects.filter(condition='p', type='p').count()
    r_reports = Report.objects.filter(condition='p', type='r').count()
    b_reports = Report.objects.filter(condition='p', type='b').count()
    projects = Projects.objects.filter(condition='a').count()
    all = projects + b_reports + r_reports + p_reports
    if all > 0:
        admins = User.objects.filter(is_staff=True)
        bot = telegram.Bot(token=ADMIN_BOT)
        for admin in admins:
            try:
                bot.send_message(chat_id=admin.username,text=f'New projects : {projects}\n'
                    f'New project reports : {p_reports}\nNew request reports : {r_reports}\nNew bug Reports : {b_reports}',
                     reply_markup=InlineKeyboardMarkup([
                         [InlineKeyboardButton('New Projects',callback_data='newProjects')],
                         [InlineKeyboardButton('Project reports',callback_data='pReports')],
                         [InlineKeyboardButton('request reports',callback_data='rReports')],
                         [InlineKeyboardButton('bug reports',callback_data='bReports')],]))
            except:
                pass

