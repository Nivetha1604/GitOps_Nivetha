from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .models import User, Transaction
from django.contrib import messages


def landing_home(request):
    return render(request, 'landing_home.html')


def login_user(request):
    if request.session.get('user_id'):
        return redirect('wallet_main')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email, password=password)
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name
            request.session['user_email'] = user.email
            return redirect('wallet_main')
        except User.DoesNotExist:
            return render(request, 'login.html', {'message': 'Invalid credentials'})

    return render(request, 'login.html')


def logout_user(request):
    request.session.flush()
    return redirect('login')


def show_register_form(request):
    request.session.flush()
    return render(request, 'register_user.html')


def register_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            return render(request, 'register_user.html', {'error': 'Email already exists.'})

        user = User(name=name, email=email, phone=phone, password=password)
        user.save()
        return redirect('login')

    return render(request, 'register_user.html')


def upload_profile_picture(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.session.get('user_id'))
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
            user.save()
        return redirect('wallet_main')


def settings_page(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    return render(request, 'settings.html', {'user': user})


def update_settings(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        password = request.POST.get('password')
        if password:
            user.password = password 

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        return redirect('wallet_main')

    return redirect('settings')

def wallet_main(request):
    user_id = request.session.get('user_id')
    user_email = request.session.get('user_email')

    if not user_id or not user_email:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
        transactions = Transaction.objects.filter(user=user).order_by('-timestamp')
    except User.DoesNotExist:
        return redirect('login')

    return render(request, 'digital_wallet_main.html', {'user': user, 'transactions': transactions})



def add_funds(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return render(request, 'add_funds.html', {'user': user, 'error': 'Please enter a valid amount.'})

        user.balance += amount
        user.save()

        Transaction.objects.create(
            user=user,
            transaction_type='ADD',
            amount=amount,
            party='Self'
        )

        return render(request, 'add_funds.html', {'user': user, 'message': 'Funds added successfully!'})

    return render(request, 'add_funds.html', {'user': user})

def transfer_money(request):
    sender_id = request.session.get('user_id')
    if not sender_id:
        return redirect('login')

    try:
        sender = User.objects.get(id=sender_id)
    except User.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email')
        try:
            amount = float(request.POST.get('amount'))
        except (ValueError, TypeError):
            return render(request, 'transfer_money.html', {'error': 'Invalid amount entered.'})

        try:
            recipient = User.objects.get(email=recipient_email)

            if sender.balance is None or sender.balance < amount:
                return render(request, 'transfer_money.html', {'error': 'Insufficient balance'})

            
            sender.balance -= amount
            recipient.balance = (recipient.balance or 0) + amount

            sender.save()
            recipient.save()

            
            Transaction.objects.create(
                user=sender,
                transaction_type='TRANSFER',
                amount=amount,
                party=recipient.email
            )

            
            Transaction.objects.create(
                user=recipient,
                transaction_type='ADD',
                amount=amount,
                party=sender.email
            )

            return render(request, 'transfer_money.html', {
                'message': f'Transferred ${amount:.2f} to {recipient.name} successfully!'
            })

        except User.DoesNotExist:
            return render(request, 'transfer_money.html', {'error': 'Recipient does not exist.'})

    return render(request, 'transfer_money.html')


def merchant_payment(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        merchant = request.POST.get('merchant')
        amount = float(request.POST.get('amount'))

        try:
            user = User.objects.get(id=user_id)
            if user.balance >= amount:
                user.balance -= amount
                user.save()

                Transaction.objects.create(
                    user=user,
                    transaction_type='MERCHANT',
                    amount=amount,
                    party=merchant
                )

                message = f"Paid ${amount} to {merchant} successfully!"
            else:
                message = "Insufficient funds."
        except User.DoesNotExist:
            message = "User not found."

        return render(request, 'merchant_payment.html', {'message': message})

    return render(request, 'merchant_payment.html')


def view_transactions(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
        transactions = Transaction.objects.filter(user=user).order_by('-timestamp')
    except User.DoesNotExist:
        return redirect('login')

    return render(request, 'view_transactions.html', {'transactions': transactions})


def process_wallet_form(request):
    if request.method == 'GET':
        selected_option = request.GET.get('walletform')

        if selected_option == 'add_funds':
            return redirect('add_funds')
        elif selected_option == 'transfer_money':
            return redirect('transfer_money')
        elif selected_option == 'merchant_payment':
            return redirect('merchant_payment')
        elif selected_option == 'view_transactions':
            return redirect('view_transactions')
        else:
            return redirect('wallet_main')










