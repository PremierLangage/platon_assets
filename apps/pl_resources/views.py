import json
from typing import Optional

import dgeq
from channels.db import database_sync_to_async
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, JsonResponse
from django.shortcuts import render

from common.async_db import has_perm_async
from common.enums import ErrorCode
from common.mixins import AsyncView
from common.validators import check_unknown_fields, check_unknown_missing_fields
from .models import Circle, Resource, File


