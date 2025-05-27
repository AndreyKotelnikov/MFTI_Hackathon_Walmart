from datetime import timedelta
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db import transaction
from django.db.models import Q
from django.db.models.aggregates import Count
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet, ViewSet
from api.models import PredictionResearch
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
from rest_framework import status

from rest_framework.decorators import action
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from api.services.predictions import get_research_predictions
from api.services.predictions import create_research_predictions
from api.services.machine_learning import process_predictions_with_ml
from api.services.machine_learning import get_prediction_shap

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
    queryset = PredictionResearch.objects.all()
    pagination_class = StandardResultsSetPagination
    def get_serializer_class(self):
        if self.request.method == 'GET' and 'pk' in self.kwargs:
            return api_serializers.PredictionResearchSerializer
        return api_serializers.PredictionListSerializer

    def list(self, request, *args, **kwargs):
        research_id = request.GET.get('research_id')
        queryset = PredictionResearch.objects.all().select_related('real')
        
        if research_id:
            queryset = queryset.filter(research_id=research_id)

        page = self.paginate_queryset(queryset)
        serializer = api_serializers.PredictionListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Проверяем и заполняем поле shap при необходимости
        print('instance.shap', instance.shap)
        if not instance.shap:
            instance.shap = get_prediction_shap(instance.id)
            instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)            

class StoreListView(ListAPIView):
    serializer_class = api_serializers.StoreSerializer
    queryset = Store.objects.all()


from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Research
from .serializers import ResearchSerializer

class ResearchViewSet(ModelViewSet):
    queryset = Research.objects.all().order_by('-created_at')
    serializer_class = ResearchSerializer
    authentication_classes = []
    permission_classes = []

    def create(self, request, *args, **kwargs):
        """
        Кастомный метод создания исследования
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        research = serializer.save()
        real_predictions = get_research_predictions(research)
        research_predictions = create_research_predictions(research, real_predictions)
        process_predictions_with_ml(research)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            # headers=headers
        )
