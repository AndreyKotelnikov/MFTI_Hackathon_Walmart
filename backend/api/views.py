from datetime import timedelta
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db import transaction
from django.db.models import Q
from django.db.models.aggregates import Count
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet, ViewSet
from api.models import PredictionWithout
from api.models import PredictionReal
from api.models import MeteoStation
from api.models import Store
from django.db.models import Q

from api.paginators import StandardResultsSetPagination
from api import serializers as api_serializers

import random
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rest_framework.decorators import action
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from api.services.machine_learning import get_customer_xdata
from api.services.machine_learning import normalize_customer_xdata
from api.services.machine_learning import load_ml_model
from api.services.machine_learning import get_predict_interpretation
from api.services.machine_learning import get_xdata_properties
from api.services.reports import churn_sales_report

from django.contrib.auth import authenticate, get_user_model
User = get_user_model()
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_201_CREATED
)


class SearchPredictionViewSet(ModelViewSet):
    queryset = PredictionReal.objects.all()
    pagination_class = StandardResultsSetPagination
    def get_serializer_class(self):
        if self.request.method == 'GET' and 'pk' in self.kwargs:
            return api_serializers.PredictionRealSerializer
        return api_serializers.PredictionListSerializer

    def list(self, request, *args, **kwargs):
        queryset = PredictionReal.objects.all()
        # queryset = queryset.order_by('prediction_date')
        page = self.paginate_queryset(queryset)
        serializer = api_serializers.PredictionListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class StoreListView(ListAPIView):
    serializer_class = api_serializers.StoreSerializer
    queryset = Store.objects.all()

