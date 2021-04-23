import datetime

from django.db.migrations import serializer
from django.db.models import Q
from rest_framework import viewsets, mixins, status
from django.shortcuts import render
from django.utils import timezone
from rest_framework.decorators import api_view, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, viewsets, status
from datetime import timedelta
from .models import Category, Post, PostImage, Like, Comment, Favorite, Rating
from .parsing import pars
from .serializers import CategorySerializer, PostSerializer, PostImageSerializer, LikeSerializer, CommentSerializer, \
    FavoriteSerializer, RatingSerializer, ParsSerializer
from rest_framework.pagination import PageNumberPagination
from .permissions import IsPostAuthor, IsAuthorPermission


class MyPaginationClass(PageNumberPagination):
    def get_pagination_response(self, data):
        return super().get_pagination_response(data)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny, ]


class PostsViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorPermission]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_permissions(self):
        """переопределим данный метод"""
        if self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsPostAuthor, ]
        else:
            permissions = [IsAuthenticated, ]
        return [permission() for permission in permissions]

    def get_queryset(self):
        queryset = super().get_queryset()
        days_count = int(self.request.query_params.get('days', 10))
        if days_count > 0:
            start_date = timezone.now() - timedelta(days=days_count)
            queryset = queryset.filter(created_at__gte=start_date)
        elif days_count == 0:
            start_date = timezone.now().date()
            queryset = queryset.filter(created_at__icontains=start_date)
        return queryset

    @action(detail=False, methods=['get'])
    def own(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(author=request.user)
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])     # router builds path posts/search/
    def search(self, request, pk=None):
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) | Q(text__icontains=q))
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def sort(self, request):
        filter_ = request.query_params.get('filter')
        if filter_ == 'A-Z':
            queryset = self.get_queryset().order_by('title')
        elif filter_ == 'Z-A':
            queryset = self.get_queryset().order_by('-title')
        else:
            queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostImageView(generics.ListCreateAPIView):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer

    def get_serializer_context(self):
        return {'request': self.request}


class LikeViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthorPermission]

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class FavoriteViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user=request.user)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class RatingViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}



class ParsOcView(APIView):
    def get(self, request):
        dict_ = pars()
        serializer = ParsSerializer(instance=dict_, many=True)
        return Response(serializer.data)