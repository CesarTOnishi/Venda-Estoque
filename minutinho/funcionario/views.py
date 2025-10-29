from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Funcionarios
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError

@login_required(login_url="/login/")
def tabelaFuncionarios (request):
    funcionario = Funcionarios.objects.all().order_by('-id')
    if request.method == "POST":
        funcionarios_id = request.POST.get('funcionarios_id', '').strip()
        form_data = {
            'nome': request.POST.get('nome', '').strip(),
            'cpf': request.POST.get('cpf'),
            'email': request.POST.get('email', '').strip(),
            'cargo': request.POST.get('cargo', '').strip(),
            'salario': request.POST.get('salario'),
            'telefone': request.POST.get('telefone'),
            'endereco': request.POST.get('endereco', '').strip(),
            'cidade': request.POST.get('cidade', '').strip(),
            'estado': request.POST.get('estado', '').strip(),
        }
        errors=[]

        if not errors:
            if funcionarios_id:
                cadFuncionario = get_object_or_404(Funcionarios, id=funcionarios_id)

                cadFuncionarioExitente = Funcionarios.objects.filter(nome=form_data['nome']).exclude(id=funcionarios_id).first()
                
                if cadFuncionarioExitente:
                    errors.append("Já existe um Funcionário com este nome.")
                else:
                    cadFuncionario.nome = form_data['nome']
                    cadFuncionario.cpf = form_data['cpf']
                    cadFuncionario.email = form_data['email']
                    cadFuncionario.cargo = form_data['cargo']
                    cadFuncionario.salario = form_data['salario']
                    cadFuncionario.telefone = form_data['telefone']
                    cadFuncionario.endereco = form_data['endereco']
                    cadFuncionario.cidade = form_data['cidade']
                    cadFuncionario.estado = form_data['estado']
                    cadFuncionario.save()
                    
                    messages.success(request, "Funcionário atualizada com sucesso!")
                    return redirect('condicaoPagamento')

            else: 
                if Funcionarios.objects.filter(nome=form_data['nome']).exists():
                    errors.append("Já existe uma condição de pagamento com este nome.")
                else:
                    try:
                        novoFuncionario = Funcionarios(
                            nome=form_data['nome'],
                            cpf=form_data['cpf'],
                            email=form_data['email'],
                            cargo=form_data['cargo'],
                            salario=form_data['salario'],
                            telefone=form_data['telefone'],
                            endereco=form_data['endereco'],
                            cidade=form_data['cidade'],
                            estado=form_data['estado'],
                        )
                        novoFuncionario.save()

                        messages.success(request, "Funcionario cadastrada com sucesso!")
                        return redirect('tabelaFuncionarios')

                    except Exception as e:
                        errors.append(f"Erro ao salvar no banco de dados: {str(e)}")

        context = {
            'funcionario': funcionario,
            'errors': errors,
            'form_data': form_data,
            'modal_open': True 
        }
        return render(request, 'funcionarios.html', context)

    return render(request, 'funcionarios.html', {
        'funcionario': funcionario,
    })

@login_required(login_url="/login/")
def deletarFuncionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionarios, id=funcionario_id)
    try:
        funcionario.delete()
        messages.success(request, f'A condição "{funcionario.nome}" foi deletada com sucesso.')
    except ProtectedError:
        messages.error(
            request,
            f'Não foi possível deletar a condição "{funcionario.nome}" porque existem registros associados.'
        )
    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao deletar: {str(e)}')

    return redirect('tabelaFuncionarios')