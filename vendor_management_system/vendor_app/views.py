from django.utils import timezone
from vendor_app import models
from django.db.models import Avg,Count,ExpressionWrapper, F, fields
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from .serializers import VendorSerializer, PurchaseOrderSerializer, HistoricalPerformanceSerializer


class VendorListCreateView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class VendorDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class PurchaseOrderDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


class VendorPerformanceView(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = HistoricalPerformanceSerializer
    def retrieve(self, request, *args, **kwargs):
        vendor = get_object_or_404(Vendor, pk=self.kwargs['pk'])
        performance_data = self.calculate_performance_metrics(vendor)
        serializer = self.get_serializer(performance_data)
        return Response(serializer.data)

    def calculate_performance_metrics(self, vendor):
        # Calculate On-Time Delivery Rate
        total_completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed').count()
        on_time_deliveries = PurchaseOrder.objects.filter(vendor=vendor, status='completed', delivery_date__lte=F('acknowledgment_date')).count()
        on_time_delivery_rate = (on_time_deliveries / total_completed_pos) * 100 if total_completed_pos != 0 else 0.0

        # Calculate Quality Rating Average
        quality_rating_avg = PurchaseOrder.objects.filter(vendor=vendor, status='completed').aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0.0

        # Calculate Average Response Time
        rresponse_times = PurchaseOrder.objects.filter(vendor=vendor, acknowledgment_date__isnull=False).annotate(
            response_time=ExpressionWrapper(
                F('acknowledgment_date') - F('issue_date'),
                output_field=fields.DurationField()
            )
        ).aggregate(Avg('response_time'))['response_time__avg'] or 0.0


        # Calculate Fulfilment Rate
        total_po_count = PurchaseOrder.objects.filter(vendor=vendor).count()
        fulfilled_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed', quality_rating__isnull=False).count()
        fulfilment_rate = (fulfilled_pos / total_po_count) * 100 if total_po_count != 0 else 0.0

        # Update or create historical performance record
        HistoricalPerformance.objects.update_or_create(
            vendor=vendor,
            date=timezone.now(),
            defaults={
                'on_time_delivery_rate': on_time_delivery_rate,
                'quality_rating_avg': quality_rating_avg,
                'average_response_time': rresponse_times,
                'fulfilment_rate': fulfilment_rate,
            }
        )
        print(vendor,on_time_delivery_rate,quality_rating_avg,rresponse_times)

        return {
            'on_time_delivery_rate': on_time_delivery_rate,
            'quality_rating_avg': quality_rating_avg,
            'average_response_time': rresponse_times,
            'fulfilment_rate': fulfilment_rate,
        }
