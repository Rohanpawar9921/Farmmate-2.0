from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import joblib
import os
from django.conf import settings
import logging


# Fallback crop recommendation data
crops_data = [
    {'N': 90, 'P': 42, 'K': 43, 'temperature': 20.879744, 'humidity': 82.002744, 'ph': 6.502985, 'rainfall': 202.935536, 'label': 'rice'},
    {'N': 85, 'P': 58, 'K': 41, 'temperature': 21.770462, 'humidity': 80.319644, 'ph': 7.038096, 'rainfall': 226.655537, 'label': 'rice'},
    {'N': 60, 'P': 55, 'K': 44, 'temperature': 23.004459, 'humidity': 82.320763, 'ph': 7.840207, 'rainfall': 263.964248, 'label': 'rice'},
    {'N': 74, 'P': 35, 'K': 40, 'temperature': 26.491096, 'humidity': 80.158363, 'ph': 6.980401, 'rainfall': 242.864034, 'label': 'rice'},
    {'N': 78, 'P': 42, 'K': 42, 'temperature': 20.130175, 'humidity': 81.604873, 'ph': 7.628473, 'rainfall': 262.717340, 'label': 'rice'},
    {'N': 69, 'P': 37, 'K': 42, 'temperature': 22.769375, 'humidity': 84.130111, 'ph': 7.085734, 'rainfall': 173.322839, 'label': 'rice'},
    {'N': 69, 'P': 55, 'K': 44, 'temperature': 23.004459, 'humidity': 82.320763, 'ph': 7.840207, 'rainfall': 263.964248, 'label': 'rice'},
    {'N': 94, 'P': 53, 'K': 55, 'temperature': 18.873041, 'humidity': 65.976423, 'ph': 6.825493, 'rainfall': 226.655537, 'label': 'maize'},
    {'N': 78, 'P': 53, 'K': 51, 'temperature': 23.174388, 'humidity': 66.413269, 'ph': 7.071734, 'rainfall': 130.175608, 'label': 'maize'},
    {'N': 89, 'P': 58, 'K': 60, 'temperature': 23.174388, 'humidity': 66.413269, 'ph': 7.071734, 'rainfall': 130.175608, 'label': 'maize'},
    {'N': 106, 'P': 34, 'K': 32, 'temperature': 26.774637, 'humidity': 66.413269, 'ph': 6.780064, 'rainfall': 177.774744, 'label': 'maize'},
    {'N': 17, 'P': 61, 'K': 20, 'temperature': 21.770462, 'humidity': 80.319644, 'ph': 7.038096, 'rainfall': 226.655537, 'label': 'chickpea'},
    {'N': 10, 'P': 61, 'K': 20, 'temperature': 21.770462, 'humidity': 80.319644, 'ph': 7.038096, 'rainfall': 226.655537, 'label': 'chickpea'},
    {'N': 20, 'P': 67, 'K': 19, 'temperature': 21.770462, 'humidity': 80.319644, 'ph': 7.038096, 'rainfall': 226.655537, 'label': 'kidneybeans'},
    {'N': 23, 'P': 69, 'K': 19, 'temperature': 21.770462, 'humidity': 80.319644, 'ph': 7.038096, 'rainfall': 226.655537, 'label': 'kidneybeans'},
]


def recommend_crop_fallback(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
    """Fallback recommendation using distance-based algorithm"""
    try:
        nitrogen = float(nitrogen)
        phosphorus = float(phosphorus)
        potassium = float(potassium)
        temperature = float(temperature)
        humidity = float(humidity)
        ph = float(ph)
        rainfall = float(rainfall)
        
        min_distance = float('inf')
        recommended_crop = None
        
        for crop in crops_data:
            distance = ((nitrogen - crop['N'])**2 + 
                       (phosphorus - crop['P'])**2 + 
                       (potassium - crop['K'])**2 + 
                       (temperature - crop['temperature'])**2 + 
                       (humidity - crop['humidity'])**2 + 
                       (ph - crop['ph'])**2 + 
                       (rainfall - crop['rainfall'])**2)**0.5
            
            if distance < min_distance:
                min_distance = distance
                recommended_crop = crop['label']
        
        return recommended_crop, "Distance-based Algorithm", "fallback"
    except Exception as e:
        logging.error(f"Fallback recommendation failed: {e}")
        return "rice", "Default Recommendation", "error"


@login_required(login_url='login')
def croprecommendation(request):
    return render(request, 'crop_recommendation/croprecommendation.html')


def result(request):
    # Initialize variables
    method_used = "Machine Learning Model"
    status = "primary"
    
    # Get input parameters
    if request.method == 'POST':
        nitrogen = request.POST.get('nitrogen')
        phosphorus = request.POST.get('phosphorus')
        potassium = request.POST.get('potassium')
        temperature = request.POST.get('temperature')
        humidity = request.POST.get('humidity')
        ph = request.POST.get('ph')
        rainfall = request.POST.get('rainfall')
    else:
        nitrogen = request.GET.get('nitrogen')
        phosphorus = request.GET.get('phosphorus')
        potassium = request.GET.get('potassium')
        temperature = request.GET.get('temperature')
        humidity = request.GET.get('humidity')
        ph = request.GET.get('ph')
        rainfall = request.GET.get('rainfall')
    
    lis = [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]
    
    # Try ML model first
    try:
        # Use the local model file
        model_path = os.path.join(settings.BASE_DIR, 'crop_recommendation', 'finalized_model.sav')
        
        # Fallback to the original location if local file doesn't exist
        if not os.path.exists(model_path):
            model_path = os.path.join(settings.BASE_DIR.parent, 'finalized_model.sav')
        
        if os.path.exists(model_path):
            cls = joblib.load(model_path)
            # Convert to float for ML model
            float_lis = [float(x) for x in lis]
            ans = cls.predict([float_lis])
            predicted_crop = ans[0] if len(ans) > 0 else None
            
            if predicted_crop:
                context = {
                    'ans': ans,
                    'list_values': lis,
                    'method_used': method_used,
                    'status': status,
                    'crop_name': predicted_crop
                }
                return render(request, 'crop_recommendation/result.html', context)
    
    except Exception as e:
        logging.error(f"ML model prediction failed: {e}")
    
    # Fallback to distance-based algorithm
    try:
        predicted_crop, fallback_method, fallback_status = recommend_crop_fallback(
            nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall
        )
        
        context = {
            'ans': [predicted_crop],
            'list_values': lis,
            'method_used': fallback_method,
            'status': fallback_status,
            'crop_name': predicted_crop
        }
        return render(request, 'crop_recommendation/result.html', context)
        
    except Exception as e:
        logging.error(f"All prediction methods failed: {e}")
        # Ultimate fallback
        context = {
            'ans': ['rice'],
            'list_values': lis,
            'method_used': 'Default Recommendation',
            'status': 'error',
            'crop_name': 'rice'
        }
        return render(request, 'crop_recommendation/result.html', context)
