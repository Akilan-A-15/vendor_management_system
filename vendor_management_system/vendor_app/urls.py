# vendor_app/urls.py

from django.urls import path
from .views import (
    VendorListCreateView, VendorDetailsView,
    PurchaseOrderListCreateView, PurchaseOrderDetailsView,
    VendorPerformanceView
)

urlpatterns = [
    path('api/vendors/', VendorListCreateView.as_view(), name='vendor-list-create'),
    path('api/vendors/<int:pk>/', VendorDetailsView.as_view(), name='vendor-details'),
    path('api/purchase_orders/', PurchaseOrderListCreateView.as_view(), name='purchase-order-list-create'),
    path('api/purchase_orders/<int:pk>/', PurchaseOrderDetailsView.as_view(), name='purchase-order-details'),
    path('api/vendors/<int:pk>/performance/', VendorPerformanceView.as_view(), name='vendor-performance'),
]
