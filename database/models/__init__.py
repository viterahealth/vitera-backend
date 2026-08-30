"""
Central model registry.

SQLAlchemy resolves relationship() string references (e.g. 'AuditLogs')
lazily, the first time any mapped class is queried -- and only against
classes that have actually been imported into the Python process by then.

Splitting models across many files means nothing guarantees they're all
imported together unless something does it explicitly. This file is that
something: import this package (or anything that transitively imports it,
e.g. importing `database.models` itself) early -- main.py does this
implicitly the moment any module's routes/services import a model class
via `from database.models.xxx_models import ...`, but to be safe, main.py
also imports this package directly before the app starts serving requests.
"""

from database.models.user_models import Users, UsersRole  # noqa: F401
from database.models.society_models import Societies, SocietiesStatus, Buildings  # noqa: F401
from database.models.camp_models import (  # noqa: F401
    Camps,
    CampsStatus,
    CampSlots,
    CampSlotsStatus,
    CampRegistrations,
    CampRegistrationsRegistrationSource,
    CampRegistrationsStatus,
)
from database.models.families_models import Families  # noqa: F401
from database.models.patient_models import Patients, PatientsGender  # noqa: F401
from database.models.vitals_models import Vitals, VitalsBloodSugarType  # noqa: F401
from database.models.medical_history_models import MedicalHistory  # noqa: F401
from database.models.consultations_models import Consultations, Prescriptions  # noqa: F401
from database.models.followup_models import Followups, FollowupsStatus  # noqa: F401
from database.models.notification_models import Notifications, NotificationsChannel, NotificationsStatus  # noqa: F401
from database.models.auditlogs_models import AuditLogs  # noqa: F401