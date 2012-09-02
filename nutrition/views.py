# This file is part of Workout Manager.
# 
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
import logging

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm


from nutrition.models import NutritionPlan
from nutrition.models import Meal
from nutrition.models import MealItem

from exercises.views import load_language

logger = logging.getLogger('workout_manager.custom')


@login_required
def overview(request):
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'nutrition'
    
    plans  = NutritionPlan.objects.filter(user = request.user)
    template_data['plans'] = plans
    
    return render_to_response('nutrition_overview.html',
                              template_data,
                              context_instance=RequestContext(request))

class MealForm(ModelForm):
    class Meta:
        model = Meal
        exclude=('plan',)

class MealItemForm(ModelForm):
    class Meta:
        model = MealItem
        exclude=('meal', 'order')

@login_required
def add(request):
    """Add a new nutrition plan and redirect to its page
    """
    
    plan = NutritionPlan()
    plan.user = request.user
    plan.language = load_language()
    plan.save()
    
    return HttpResponseRedirect('/nutrition/%s/view/' % plan.id)


@login_required
def view(request, id):
    """Show the nutrition plan with the given ID
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    return render_to_response('view_nutrition_plan.html', 
                              template_data,
                              context_instance=RequestContext(request))

@login_required
def edit_meal(request, id, meal_id=None):
    """Form to add a meal to a plan
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    meal = Meal()
    meal.plan = plan
    meal.order = 1
    meal.save()
    
    return HttpResponseRedirect('/nutrition/%s/view/' % plan.id)
    

@login_required
def edit_meal_item(request, id, meal_id, item_id=None):
    """Form to add a meal to a plan
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    # Load the meal
    meal = get_object_or_404(Meal, pk=meal_id)
    template_data['meal'] = meal
    
    if meal.plan != plan:
        return HttpResponseForbidden()
    
    
    # Load the meal item
    if not item_id or item_id == 'None':
        meal_item = MealItem()
    else:
        meal_item = get_object_or_404(MealItem, pk=item_id)

    template_data['meal_item'] = meal_item
    
    
    
    # Process request
    if request.method == 'POST':
        meal_form = MealItemForm(request.POST, instance=meal_item)
        
        # If the data is valid, save and redirect
        if meal_form.is_valid():
            meal_item = meal_form.save(commit=False)
            meal_item.meal = meal
            meal_item.order = 1
            meal_item.save()
            
            return HttpResponseRedirect('/nutrition/%s/view/' % id)
    else:
        meal_form = MealItemForm(instance=meal_item)
    template_data['form'] = meal_form
    
    return render_to_response('edit_meal.html', 
                              template_data,
                              context_instance=RequestContext(request))