from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, logout_user, current_user

from app import db
from app.models import User
from app.blueprints.api import bp