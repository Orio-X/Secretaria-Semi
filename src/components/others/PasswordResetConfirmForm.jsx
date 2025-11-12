import React, { useState } from 'react';

// Componente de formulário para confirmar a redefinição de senha
export default function PasswordResetConfirmForm({ token }) { 
  // Recebe o token (gerado no link de email) como uma propriedade
  
  // Estados para armazenar os valores dos campos de senha
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  
  // Estado para indicar se a requisição está em andamento (loading)
  const [isLoading, setIsLoading] = useState(false);
  // Estado para armazenar e exibir mensagens de erro
  const [error, setError] = useState(null);
  // Estado para armazenar e exibir a mensagem de sucesso
  const [successMessage, setSuccessMessage] = useState(null);

  // Função chamada ao enviar o formulário
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // --- 1. Validações Locais ---
    if (password !== passwordConfirm) { 
      setError('As senhas não coincidem.'); 
      return; 
    }
    if (password.length < 8) { 
      setError('A senha deve ter pelo menos 8 caracteres.'); 
      return; 
    }
    
    // Inicia o processo de requisição
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // --- 2. Requisição para a API de Confirmação ---
      const response = await fetch('http://localhost:8000/api/password-reset/confirm/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // Envia o token e a nova senha para o backend
        body: JSON.stringify({ token: token, password: password }),
      });
      
      const data = await response.json();
      
      // Verifica se a resposta HTTP não foi OK (status 4xx ou 5xx)
      if (!response.ok) { 
        // Lança um erro com a mensagem retornada pela API
        throw new Error(data.error || 'Ocorreu um erro.'); 
      }

      // --- 3. Sucesso ---
      setSuccessMessage('Senha redefinida com sucesso! Redirecionando para o login...');
      // Redireciona para a página de login após 3 segundos
      setTimeout(() => { window.location.href = '/login'; }, 3000);
      
    } catch (err) {
      // Captura e exibe o erro
      setError(err.message);
    } finally {
      // Finaliza o estado de loading, independentemente do sucesso ou erro
      setIsLoading(false);
    }
  };

  return (
    // Formulário de redefinição de senha
    <form className="contact-form respondForm__form row y-gap-20 pt-30" onSubmit={handleSubmit}>
      
      {/* Campo Nova Senha */}
      <div className="col-12">
        <label className="text-16 lh-1 fw-500 text-dark-1 mb-10">Nova Senha</label>
        <input 
          required 
          type="password" 
          name="password" 
          placeholder="Pelo menos 8 caracteres" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} // Atualiza o estado da senha
        />
      </div>
      
      {/* Campo Confirmação de Senha */}
      <div className="col-12">
        <label className="text-16 lh-1 fw-500 text-dark-1 mb-10">Confirme a Nova Senha</label>
        <input 
          required 
          type="password" 
          name="passwordConfirm" 
          placeholder="Repita a nova senha" 
          value={passwordConfirm} 
          onChange={(e) => setPasswordConfirm(e.target.value)} // Atualiza o estado da confirmação
        />
      </div>
      
      {/* Exibição da mensagem de sucesso */}
      {successMessage && <div className="col-12"><p className="text-green-1">{successMessage}</p></div>}
      
      {/* Exibição da mensagem de erro */}
      {error && <div className="col-12"><p className="text-red-1">{error}</p></div>}
      
      {/* Botão de Envio */}
      <div className="col-12">
        <button 
          type="submit" 
          className="button -md -green-1 text-dark-1 fw-500 w-1/1" 
          // Desabilita o botão se estiver carregando ou se o sucesso já foi alcançado
          disabled={isLoading || successMessage}
        >
          {/* Altera o texto do botão com base no estado de loading */}
          {isLoading ? 'Salvando...' : 'Salvar Nova Senha'}
        </button>
      </div>
    </form>
  );
}