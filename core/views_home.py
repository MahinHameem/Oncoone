from django.shortcuts import render

def index_view(request):
    """Serve the index.html homepage."""
    return render(request, 'index.html')

def products_view(request):
    """Serve the products.html page."""
    return render(request, 'products.html')

