import React, { useState } from 'react';

// Componente de formulário para solicitar a redefinição de senha
export default function PasswordResetRequestForm() {
  // Estado para armazenar o email digitado pelo usuário
  const [email, setEmail] = useState('');
  // Estado para indicar se a requisição está em andamento (loading)
  const [isLoading, setIsLoading] = useState(false);
  // Estado para armazenar e exibir mensagens de erro
  const [error, setError] = useState(null);
  // Estado para armazenar e exibir a mensagem de sucesso (ex: "E-mail enviado")
  const [successMessage, setSuccessMessage] = useState(null);

  // Função chamada ao enviar o formulário
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Inicia o estado de carregamento e limpa mensagens anteriores
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // --- 1. Requisição para a API de Solicitação de Redefinição ---
      const response = await fetch('http://localhost:8000/api/password-reset/request/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // Envia o email digitado para o backend
        body: JSON.stringify({ email }),
      });
      
      const data = await response.json();

      // Verifica se a resposta HTTP não foi OK (indicando erro)
      if (!response.ok) { 
        // Lança um erro com a mensagem retornada pela API
        throw new Error(data.error || 'Ocorreu um erro.'); 
      }

      // --- 2. Sucesso ---
      // Define a mensagem de sucesso que a API retornou (ex: "Verifique seu email")
      setSuccessMessage(data.success);
      
    } catch (err) {
      // Captura e exibe o erro
      setError(err.message);
    } finally {
      // Finaliza o estado de loading
      setIsLoading(false);
    }
  };

  return (
    // Formulário de solicitação de redefinição de senha
    <form className="contact-form respondForm__form row y-gap-20 pt-30" onSubmit={handleSubmit}>
      
      {/* Campo de E-mail */}
      <div className="col-12">
        <label className="text-16 lh-1 fw-500 text-dark-1 mb-10">Digite seu E-mail de Cadastro</label>
        <input 
          required 
          type="email" 
          name="email" 
          placeholder="seu@email.com" 
          value={email} 
          onChange={(e) => setEmail(e.target.value)} // Atualiza o estado do email
        />
      </div>
      
      {/* Exibição da mensagem de sucesso (ex: "Link enviado") */}
      {successMessage && <div className="col-12"><p className="text-green-1">{successMessage}</p></div>}
      
      {/* Exibição da mensagem de erro */}
      {error && <div className="col-12"><p className="text-red-1">{error}</p></div>}
      
      {/* Botão de Envio */}
      <div className="col-12">
        <button 
          type="submit" 
          className="button -md -green-1 text-dark-1 fw-500 w-1/1" 
          // Desabilita o botão se estiver carregando ou se a mensagem de sucesso já foi exibida
          disabled={isLoading || successMessage}
        >
          {/* Altera o texto do botão com base no estado de loading */}
          {isLoading ? 'Enviando...' : 'Enviar Link de Redefinição'}
        </button>
      </div>
    </form>
  );
}