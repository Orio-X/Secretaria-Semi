from datetime import date, time
from unittest.mock import patch

from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from secretaria.models import (
    Responsavel,
    Aluno,
    Professor,
    PasswordResetToken,
    PlanejamentoSemanal,
)
from secretaria.validators import validar_cpf, validar_telefone

class ResponsavelModelTest(TestCase):
    """
    Testes para o modelo Responsavel.
    """

    def test_responsavel_criacao(self):
        """
        Verifica se um Responsavel pode ser criado com sucesso.
        """
        responsavel = Responsavel.objects.create(
            name="João da Silva",
            phone_number="62998765432",
            email="joao@example.com",
            adress="Rua das Flores, 123",
            cpf="12345678901",
            birthday="1980-01-01"
        )
        self.assertEqual(responsavel.name, "João da Silva")
        self.assertEqual(responsavel.cpf, "12345678901")
        self.assertIsInstance(responsavel, Responsavel)

    def test_responsavel_str_representacao(self):
        """
        Verifica a representação em string do modelo Responsavel.
        """
        responsavel = Responsavel.objects.create(
            name="Maria Santos",
            phone_number="62987654321",
            email="maria@example.com",
            adress="Avenida Central, 456",
            cpf="98765432109",
            birthday="1985-05-15"
        )
        self.assertEqual(str(responsavel), "Maria Santos")

    def test_responsavel_cpf_invalido(self):
        """
        Verifica se a validação de CPF funciona corretamente (testando um CPF repetido).
        """
        Responsavel.objects.create(
            name="Carlos Pereira",
            phone_number="62912345678",
            email="carlos@example.com",
            adress="Travessa da Paz, 789",
            cpf="11122233344",
            birthday="1990-10-20"
        )
        # Tenta criar um segundo responsavel com o mesmo CPF.
        with self.assertRaises(Exception): # Usar Exception é mais genérico, mas pode ser mais específico.
            Responsavel.objects.create(
                name="Ana Costa",
                phone_number="62923456789",
                email="ana@example.com",
                adress="Alameda dos Pinheiros, 101",
                cpf="11122233344",
                birthday="1992-12-25"
            )

class AlunoModelTest(TestCase):
    """
    Testes para o modelo Aluno.
    """

    def setUp(self):
        # Cria um responsável que será usado em todos os testes de aluno.
        self.responsavel = Responsavel.objects.create(
            name="Carlos Oliveira",
            phone_number="62933334444",
            email="carlos.o@example.com",
            adress="Rua Teste, 50",
            cpf="11111111111",
            birthday="1975-02-28"
        )

    def test_aluno_criacao(self):
        """
        Verifica se um Aluno pode ser criado com sucesso.
        """
        aluno = Aluno.objects.create(
            name_aluno="Pedro Diniz",
            phone_number_aluno="62955556666",
            email_aluno="pedro.d@example.com",
            cpf_aluno="22222222222",
            birthday_aluno="2005-03-10",
            class_choice="1A",
            month_choice="02",
            faltas_aluno="0",
            Responsavel=self.responsavel
        )
        self.assertEqual(aluno.name_aluno, "Pedro Diniz")
        self.assertEqual(aluno.Responsavel.name, "Carlos Oliveira")
        self.assertIsInstance(aluno, Aluno)

    def test_media_por_disciplina(self):
        """
        Verifica se o método media_por_disciplina calcula a média corretamente.
        """
        aluno = Aluno.objects.create(
            name_aluno="Larissa Lima",
            phone_number_aluno="62977778888",
            email_aluno="larissa.l@example.com",
            cpf_aluno="33333333333",
            birthday_aluno="2006-07-22",
            class_choice="2B",
            month_choice="03",
            faltas_aluno="2",
            Responsavel=self.responsavel
        )
        from .models import Bimestre, Nota
        bimestre1 = Bimestre.objects.create(numero=1)
        bimestre2 = Bimestre.objects.create(numero=2)

        Nota.objects.create(aluno=aluno, bimestre=bimestre1, valor=8.0, disciplina='MAT')
        Nota.objects.create(aluno=aluno, bimestre=bimestre2, valor=9.0, disciplina='MAT')

        media = aluno.media_por_disciplina('MAT')
        self.assertEqual(media, 8.5)


class PasswordResetRequestViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('password_reset_request')
        for group_name in ['Responsavel', 'Aluno', 'Professor', 'Secretaria', 'Auxiliar administrativo']:
            Group.objects.get_or_create(name=group_name)

    def test_password_reset_for_user_email(self):
        user = User.objects.create_user(username='direct', email='direct@example.com', password='password123')
        old_token = PasswordResetToken.objects.create(user=user)

        with patch('secretaria.views.send_mail') as mocked_send_mail:
            response = self.client.post(self.url, {'email': 'direct@example.com'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(PasswordResetToken.objects.filter(id=old_token.id).exists())
        tokens = PasswordResetToken.objects.filter(user=user)
        self.assertEqual(tokens.count(), 1)
        mocked_send_mail.assert_called_once()
        self.assertEqual(mocked_send_mail.call_args[0][3], ['direct@example.com'])

    def test_password_reset_for_responsavel_email(self):
        user = User.objects.create_user(username='resp_user', email='', password='password123')
        responsavel = Responsavel.objects.create(
            user=user,
            name='Responsavel Um',
            phone_number='62900000001',
            email='responsavel@example.com',
            adress='Rua A, 123',
            cpf='12345678901',
            birthday=date(1980, 1, 1),
        )
        Aluno.objects.create(
            user=None,
            name_aluno='Aluno Dependente',
            phone_number_aluno='62900000014',
            email_aluno='dependente-resp@example.com',
            cpf_aluno='98765432111',
            birthday_aluno=date(2010, 2, 2),
            class_choice='1A',
            month_choice='01',
            Responsavel=responsavel,
        )

        with patch('secretaria.views.send_mail') as mocked_send_mail:
            response = self.client.post(self.url, {'email': responsavel.email}, format='json')

        self.assertEqual(response.status_code, 200)
        tokens = PasswordResetToken.objects.filter(user=user)
        self.assertEqual(tokens.count(), 1)
        self.assertTrue(user.groups.filter(name='Responsavel').exists())
        mocked_send_mail.assert_called_once()
        self.assertEqual(mocked_send_mail.call_args[0][3], [responsavel.email])

        token = tokens.first()
        new_password = 'SenhaResponsavelExistente123'
        confirm_response = self.client.post(
            reverse('password_reset_confirm'),
            {'token': str(token.token), 'password': new_password},
            format='json',
        )
        self.assertEqual(confirm_response.status_code, 200)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            {'cpf': responsavel.cpf, 'password': new_password},
            format='json',
        )
        self.assertEqual(login_response.status_code, 200)

        access_token = login_response.data['access']
        auth_client = APIClient()
        auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_response = auth_client.get(reverse('aluno-list'))
        self.assertEqual(list_response.status_code, 200)

    def test_password_reset_auto_links_responsavel_without_user(self):
        responsavel = Responsavel.objects.create(
            user=None,
            name='Responsavel Sem Usuario',
            phone_number='62900000005',
            email='responsavel-sem-user@example.com',
            adress='Rua C, 789',
            cpf='12345678905',
            birthday=date(1982, 5, 5),
        )
        Aluno.objects.create(
            user=None,
            name_aluno='Aluno Dependente',
            phone_number_aluno='62900000015',
            email_aluno='dependente@example.com',
            cpf_aluno='98765432100',
            birthday_aluno=date(2010, 1, 1),
            class_choice='1A',
            month_choice='01',
            Responsavel=responsavel,
        )

        with patch('secretaria.views.send_mail') as mocked_send_mail:
            response = self.client.post(self.url, {'email': responsavel.email}, format='json')

        self.assertEqual(response.status_code, 200)
        responsavel.refresh_from_db()
        self.assertIsNotNone(responsavel.user)
        self.assertEqual(responsavel.user.username, responsavel.cpf)
        self.assertEqual(responsavel.user.email, responsavel.email)
        self.assertTrue(responsavel.user.groups.filter(name='Responsavel').exists())
        tokens = PasswordResetToken.objects.filter(user=responsavel.user)
        self.assertEqual(tokens.count(), 1)
        mocked_send_mail.assert_called_once()
        self.assertEqual(mocked_send_mail.call_args[0][3], [responsavel.email])

        token = tokens.first()
        new_password = 'SenhaResponsavel123'
        confirm_response = self.client.post(
            reverse('password_reset_confirm'),
            {'token': str(token.token), 'password': new_password},
            format='json',
        )
        self.assertEqual(confirm_response.status_code, 200)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            {'cpf': responsavel.cpf, 'password': new_password},
            format='json',
        )
        self.assertEqual(login_response.status_code, 200)

        access_token = login_response.data['access']
        auth_client = APIClient()
        auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_response = auth_client.get(reverse('aluno-list'))
        self.assertEqual(list_response.status_code, 200)

    def test_password_reset_for_aluno_email(self):
        responsavel = Responsavel.objects.create(
            user=None,
            name='Responsavel Dois',
            phone_number='62900000002',
            email='responsavel2@example.com',
            adress='Rua B, 456',
            cpf='12345678902',
            birthday=date(1981, 2, 2),
        )
        user = User.objects.create_user(username='aluno_user', email='', password='password123')
        aluno = Aluno.objects.create(
            user=user,
            name_aluno='Aluno Teste',
            phone_number_aluno='62900000003',
            email_aluno='aluno@example.com',
            cpf_aluno='12345678903',
            birthday_aluno=date(2005, 3, 3),
            class_choice='1A',
            month_choice='01',
            Responsavel=responsavel,
        )

        with patch('secretaria.views.send_mail') as mocked_send_mail:
            response = self.client.post(self.url, {'email': aluno.email_aluno}, format='json')

        self.assertEqual(response.status_code, 200)
        tokens = PasswordResetToken.objects.filter(user=user)
        self.assertEqual(tokens.count(), 1)
        self.assertTrue(user.groups.filter(name='Aluno').exists())
        mocked_send_mail.assert_called_once()
        self.assertEqual(mocked_send_mail.call_args[0][3], [aluno.email_aluno])

        token = tokens.first()
        new_password = 'SenhaAlunoExistente123'
        confirm_response = self.client.post(
            reverse('password_reset_confirm'),
            {'token': str(token.token), 'password': new_password},
            format='json',
        )
        self.assertEqual(confirm_response.status_code, 200)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            {'cpf': aluno.cpf_aluno, 'password': new_password},
            format='json',
        )
        self.assertEqual(login_response.status_code, 200)

        access_token = login_response.data['access']
        auth_client = APIClient()
        auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_response = auth_client.get(reverse('aluno-list'))
        self.assertEqual(list_response.status_code, 200)

    def test_password_reset_auto_links_aluno_without_user(self):
        responsavel = Responsavel.objects.create(
            user=None,
            name='Responsavel Tres',
            phone_number='62900000006',
            email='responsavel3@example.com',
            adress='Rua D, 101',
            cpf='12345678906',
            birthday=date(1983, 6, 6),
        )
        aluno = Aluno.objects.create(
            user=None,
            name_aluno='Aluno Sem Usuario',
            phone_number_aluno='62900000007',
            email_aluno='aluno-sem-user@example.com',
            cpf_aluno='12345678907',
            birthday_aluno=date(2006, 7, 7),
            class_choice='1A',
            month_choice='01',
            Responsavel=responsavel,
        )

        with patch('secretaria.views.send_mail') as mocked_send_mail:
            response = self.client.post(self.url, {'email': aluno.email_aluno}, format='json')

        self.assertEqual(response.status_code, 200)
        aluno.refresh_from_db()
        self.assertIsNotNone(aluno.user)
        self.assertEqual(aluno.user.username, aluno.cpf_aluno)
        self.assertEqual(aluno.user.email, aluno.email_aluno)
        self.assertTrue(aluno.user.groups.filter(name='Aluno').exists())
        tokens = PasswordResetToken.objects.filter(user=aluno.user)
        self.assertEqual(tokens.count(), 1)
        mocked_send_mail.assert_called_once()
        self.assertEqual(mocked_send_mail.call_args[0][3], [aluno.email_aluno])

        token = tokens.first()
        new_password = 'SenhaAluno123'
        confirm_response = self.client.post(
            reverse('password_reset_confirm'),
            {'token': str(token.token), 'password': new_password},
            format='json',
        )
        self.assertEqual(confirm_response.status_code, 200)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            {'cpf': aluno.cpf_aluno, 'password': new_password},
            format='json',
        )
        self.assertEqual(login_response.status_code, 200)

        access_token = login_response.data['access']
        auth_client = APIClient()
        auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_response = auth_client.get(reverse('aluno-list'))
        self.assertEqual(list_response.status_code, 200)

    def test_password_reset_for_professor_email(self):
        user = User.objects.create_user(username='prof_user', email='', password='password123')
        professor = Professor.objects.create(
            user=user,
            disciplina='MAT',
            name_professor='Professor Teste',
            phone_number_professor='62900000004',
            email_professor='prof@example.com',
            cpf_professor='12345678904',
            birthday_professor=date(1975, 4, 4),
            matricula_professor='MAT12345678',
        )
        responsavel = Responsavel.objects.create(
            user=None,
            name='Responsavel Professor',
            phone_number='62900000016',
            email='responsavel-prof@example.com',
            adress='Rua J, 707',
            cpf='55555555555',
            birthday=date(1980, 1, 1),
        )
        Aluno.objects.create(
            user=None,
            name_aluno='Aluno Professor',
            phone_number_aluno='62900000017',
            email_aluno='aluno-prof@example.com',
            cpf_aluno='22222222222',
            birthday_aluno=date(2008, 8, 8),
            class_choice='1A',
            month_choice='01',
            Responsavel=responsavel,
        )
        PlanejamentoSemanal.objects.create(
            professor=professor,
            turma='1A',
            disciplina='Matemática',
            dia_semana='SEG',
            data_aula=date(2024, 1, 1),
            turno='MANHA',
            horario_inicio=time(8, 0),
            horario_fim=time(9, 0),
            conteudo='Conteúdo',
            atividades='',
            recursos='',
            observacoes='',
        )

        with patch('secretaria.views.send_mail') as mocked_send_mail:
            response = self.client.post(self.url, {'email': professor.email_professor}, format='json')

        self.assertEqual(response.status_code, 200)
        tokens = PasswordResetToken.objects.filter(user=user)
        self.assertEqual(tokens.count(), 1)
        self.assertTrue(user.groups.filter(name='Professor').exists())
        mocked_send_mail.assert_called_once()
        self.assertEqual(mocked_send_mail.call_args[0][3], [professor.email_professor])

        token = tokens.first()
        new_password = 'SenhaProfessorExistente123'
        confirm_response = self.client.post(
            reverse('password_reset_confirm'),
            {'token': str(token.token), 'password': new_password},
            format='json',
        )
        self.assertEqual(confirm_response.status_code, 200)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            {'cpf': professor.cpf_professor, 'password': new_password},
            format='json',
        )
        self.assertEqual(login_response.status_code, 200)

        access_token = login_response.data['access']
        auth_client = APIClient()
        auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_response = auth_client.get(reverse('aluno-list'))
        self.assertEqual(list_response.status_code, 200)

    def test_password_reset_auto_links_professor_without_user(self):
        professor = Professor.objects.create(
            user=None,
            disciplina='MAT',
            name_professor='Professor Sem Usuario',
            phone_number_professor='62900000008',
            email_professor='professor-sem-user@example.com',
            cpf_professor='12345678908',
            birthday_professor=date(1976, 8, 8),
            matricula_professor='MAT87654321',
        )
        responsavel = Responsavel.objects.create(
            user=None,
            name='Responsavel Professor Sem Usuario',
            phone_number='62900000018',
            email='responsavel-prof-sem-user@example.com',
            adress='Rua K, 808',
            cpf='66666666666',
            birthday=date(1981, 2, 2),
        )
        Aluno.objects.create(
            user=None,
            name_aluno='Aluno Professor Sem Usuario',
            phone_number_aluno='62900000019',
            email_aluno='aluno-prof-sem-user@example.com',
            cpf_aluno='33333333333',
            birthday_aluno=date(2009, 9, 9),
            class_choice='1A',
            month_choice='01',
            Responsavel=responsavel,
        )
        PlanejamentoSemanal.objects.create(
            professor=professor,
            turma='1A',
            disciplina='Matemática',
            dia_semana='TER',
            data_aula=date(2024, 1, 2),
            turno='MANHA',
            horario_inicio=time(9, 0),
            horario_fim=time(10, 0),
            conteudo='Conteúdo',
            atividades='',
            recursos='',
            observacoes='',
        )

        with patch('secretaria.views.send_mail') as mocked_send_mail:
            response = self.client.post(self.url, {'email': professor.email_professor}, format='json')

        self.assertEqual(response.status_code, 200)
        professor.refresh_from_db()
        self.assertIsNotNone(professor.user)
        self.assertEqual(professor.user.username, professor.cpf_professor)
        self.assertEqual(professor.user.email, professor.email_professor)
        self.assertTrue(professor.user.groups.filter(name='Professor').exists())
        tokens = PasswordResetToken.objects.filter(user=professor.user)
        self.assertEqual(tokens.count(), 1)
        mocked_send_mail.assert_called_once()
        self.assertEqual(mocked_send_mail.call_args[0][3], [professor.email_professor])

        token = tokens.first()
        new_password = 'SenhaProfessor123'
        confirm_response = self.client.post(
            reverse('password_reset_confirm'),
            {'token': str(token.token), 'password': new_password},
            format='json',
        )
        self.assertEqual(confirm_response.status_code, 200)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            {'cpf': professor.cpf_professor, 'password': new_password},
            format='json',
        )
        self.assertEqual(login_response.status_code, 200)

        access_token = login_response.data['access']
        auth_client = APIClient()
        auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        list_response = auth_client.get(reverse('aluno-list'))
        self.assertEqual(list_response.status_code, 200)

    def test_password_reset_flow_allows_login_with_cpf_after_confirm(self):
        responsavel = Responsavel.objects.create(
            user=None,
            name='Responsavel Login',
            phone_number='62900000009',
            email='responsavel-login@example.com',
            adress='Rua E, 202',
            cpf='12345678909',
            birthday=date(1984, 9, 9),
        )

        with patch('secretaria.views.send_mail'):
            request_response = self.client.post(self.url, {'email': responsavel.email}, format='json')

        self.assertEqual(request_response.status_code, 200)
        responsavel.refresh_from_db()
        self.assertIsNotNone(responsavel.user)
        self.assertEqual(responsavel.user.username, responsavel.cpf)

        token = PasswordResetToken.objects.get(user=responsavel.user)
        confirm_url = reverse('password_reset_confirm')
        new_password = 'NovaSenhaSegura123'

        confirm_response = self.client.post(
            confirm_url,
            {'token': str(token.token), 'password': new_password},
            format='json',
        )

        self.assertEqual(confirm_response.status_code, 200)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            {'cpf': responsavel.cpf, 'password': new_password},
            format='json',
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)

    def test_password_reset_normalizes_existing_username_and_allows_login(self):
        original_user = User.objects.create_user(
            username='responsavel-slug',
            email='',
            password='SenhaAntiga123',
        )
        responsavel = Responsavel.objects.create(
            user=original_user,
            name='Responsavel Antigo',
            phone_number='62900000010',
            email='responsavel-antigo@example.com',
            adress='Rua F, 303',
            cpf='12345678910',
            birthday=date(1985, 10, 10),
        )

        with patch('secretaria.views.send_mail'):
            request_response = self.client.post(self.url, {'email': responsavel.email}, format='json')

        self.assertEqual(request_response.status_code, 200)
        responsavel.refresh_from_db()
        self.assertEqual(responsavel.user.pk, original_user.pk)
        self.assertEqual(responsavel.user.username, responsavel.cpf)
        self.assertEqual(responsavel.user.email, responsavel.email)

        token = PasswordResetToken.objects.get(user=responsavel.user)
        confirm_url = reverse('password_reset_confirm')
        new_password = 'SenhaNormalizada456'

        confirm_response = self.client.post(
            confirm_url,
            {'token': str(token.token), 'password': new_password},
            format='json',
        )

        self.assertEqual(confirm_response.status_code, 200)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            {'cpf': responsavel.cpf, 'password': new_password},
            format='json',
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)

    def test_password_reset_normalizes_user_found_by_email_and_allows_login(self):
        original_user = User.objects.create_user(
            username='responsavel-email-slug',
            email='responsavel-email-match@example.com',
            password='SenhaAntiga123',
        )
        responsavel = Responsavel.objects.create(
            user=original_user,
            name='Responsavel Email Match',
            phone_number='62900000013',
            email=original_user.email,
            adress='Rua I, 606',
            cpf='12345678913',
            birthday=date(1988, 1, 13),
        )

        with patch('secretaria.views.send_mail'):
            request_response = self.client.post(self.url, {'email': responsavel.email}, format='json')

        self.assertEqual(request_response.status_code, 200)
        responsavel.refresh_from_db()
        self.assertEqual(responsavel.user.pk, original_user.pk)
        self.assertEqual(responsavel.user.username, responsavel.cpf)
        self.assertEqual(responsavel.user.email, responsavel.email)

        token = PasswordResetToken.objects.get(user=responsavel.user)
        new_password = 'SenhaEmailMatch135'

        confirm_response = self.client.post(
            reverse('password_reset_confirm'),
            {'token': str(token.token), 'password': new_password},
            format='json',
        )

        self.assertEqual(confirm_response.status_code, 200)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            {'cpf': responsavel.cpf, 'password': new_password},
            format='json',
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)

    def test_login_accepts_cpf_with_mask_after_password_reset(self):
        responsavel = Responsavel.objects.create(
            user=None,
            name='Responsavel CPF Mask',
            phone_number='62900000011',
            email='responsavel-mask@example.com',
            adress='Rua G, 404',
            cpf='12345678911',
            birthday=date(1986, 11, 11),
        )

        with patch('secretaria.views.send_mail'):
            request_response = self.client.post(self.url, {'email': responsavel.email}, format='json')

        self.assertEqual(request_response.status_code, 200)
        responsavel.refresh_from_db()

        token = PasswordResetToken.objects.get(user=responsavel.user)
        new_password = 'SenhaComMascara789'

        confirm_response = self.client.post(
            reverse('password_reset_confirm'),
            {'token': str(token.token), 'password': new_password},
            format='json',
        )

        self.assertEqual(confirm_response.status_code, 200)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            {'cpf': '123.456.789-11', 'password': new_password},
            format='json',
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)

    def test_login_rejects_email_after_password_reset(self):
        responsavel = Responsavel.objects.create(
            user=None,
            name='Responsavel Email Login',
            phone_number='62900000012',
            email='responsavel-email@example.com',
            adress='Rua H, 505',
            cpf='12345678912',
            birthday=date(1987, 12, 12),
        )

        with patch('secretaria.views.send_mail'):
            request_response = self.client.post(self.url, {'email': responsavel.email}, format='json')

        self.assertEqual(request_response.status_code, 200)
        responsavel.refresh_from_db()

        token = PasswordResetToken.objects.get(user=responsavel.user)
        new_password = 'SenhaEmail0123'

        confirm_response = self.client.post(
            reverse('password_reset_confirm'),
            {'token': str(token.token), 'password': new_password},
            format='json',
        )

        self.assertEqual(confirm_response.status_code, 200)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            {'cpf': responsavel.email, 'password': new_password},
            format='json',
        )

        self.assertEqual(login_response.status_code, 400)
        self.assertNotIn('access', login_response.data)
        self.assertNotIn('refresh', login_response.data)

    def test_password_reset_for_unknown_email(self):
        with patch('secretaria.views.send_mail') as mocked_send_mail:
            response = self.client.post(self.url, {'email': 'unknown@example.com'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PasswordResetToken.objects.count(), 0)
        mocked_send_mail.assert_not_called()
