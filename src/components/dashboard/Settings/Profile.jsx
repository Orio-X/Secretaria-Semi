import React, { useState, useEffect } from "react";
import api from "@/api/axios"; // Usando sua instância 'api'

// --- Imports do Material-UI para exibir os dados ---
import {
  Box,
  Typography,
  Grid,
  Paper,
  CircularProgress,
  Alert
} from "@mui/material";

// --- Helper de Autenticação (padrão) ---
const getAuthHeaders = () => {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    console.error("Token de autenticação não encontrado.");
    return null;
  }
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

// --- Helper para formatar a data (YYYY-MM-DD -> DD/MM/YYYY) ---
const formatDate = (dateString) => {
  if (!dateString) return "Não informada";
  try {
    // Corrigindo potencial problema de fuso horário ao exibir YYYY-MM-DD
    const [year, month, day] = dateString.split('-').map(Number);
    if (day && month && year) {
        const date = new Date(year, month - 1, day);
        return date.toLocaleDateString('pt-BR');
    }
    // Fallback para datas completas (com timestamp)
    return new Date(dateString).toLocaleDateString('pt-BR');
  } catch (e) {
    return "Data inválida";
  }
};

// --- Helper para buscar o endpoint correto ---
const getEndpointByCargo = (cargo) => {
  if (!cargo) return null;
  
  switch (cargo.toLowerCase()) {
    case 'aluno':
      return '/api/alunos/';
    case 'professor':
      return '/api/professores/';
    case 'responsavel':
      return '/api/responsaveis/';
    // Adicione outros cargos se necessário (ex: 'secretaria', 'auxiliaradmin')
    // NOTA: 'secretaria' pode não ter um endpoint de perfil dedicado.
    default:
      return null;
  }
};

// --- Componente de Campo (Apenas Leitura) ---
function ProfileField({ label, value }) {
  return (
    <Grid item xs={12} sm={6} md={4}> {/* Ajustado para 3 colunas em telas médias */}
      <Typography variant="caption" color="textSecondary" component="div">
        {label}
      </Typography>
      <Typography variant="body1" fontWeight={500} sx={{ wordBreak: 'break-word' }}>
        {value || "Não informado"}
      </Typography>
    </Grid>
  );
}

// ================================================================
// COMPONENTE PRINCIPAL DO PERFIL
// ================================================================
export default function Profile({ activeTab }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUserData = async () => {
      setLoading(true);
      setError(null);
      
      // 1. Pegar Token e Cargo do localStorage
      const headers = getAuthHeaders();
      const cargo = localStorage.getItem('userCargo');

      if (!headers) {
        setError("Usuário não autenticado. Faça o login novamente.");
        setLoading(false);
        return;
      }
      
      if (!cargo) {
        setError("Cargo do usuário não encontrado. Faça o login novamente.");
        setLoading(false);
        return;
      }

      // 2. Descobrir qual endpoint chamar
      const endpoint = getEndpointByCargo(cargo);

      if (!endpoint) {
        setError(`O perfil para o cargo "${cargo}" não está configurado para exibição.`);
        setLoading(false);
        return;
      }

      try {
        // 3. Chamar o endpoint CORRETO
        const response = await api.get(endpoint, { headers }); 
        
        // 4. A API (views.py) retorna uma LISTA (paginada ou não)
        let userData = null;
        if (response.data && Array.isArray(response.data.results)) {
            // Se for paginada (ex: /api/alunos/)
            userData = response.data.results[0]; 
        } else if (response.data && Array.isArray(response.data)) {
            // Se for uma lista simples (ex: /api/alunos/)
            userData = response.data[0];
        }

        if (!userData) {
            throw new Error("Resposta da API recebida, mas dados do usuário não encontrados.");
        }

        setUser(userData);

      } catch (err) {
        // O erro 404 (Not Found) anterior agora está corrigido.
        // O erro 403 (Forbidden) pode acontecer se a lógica de permissão estiver errada.
        console.error("Erro ao buscar dados do perfil:", err);
        setError(`Não foi possível carregar os dados do perfil (Endpoint: ${endpoint}). Verifique o console.`);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []); // Roda uma vez quando o componente é montado

  // --- Normalização dos Dados ---
  // Esta lógica permanece a mesma, lendo os diferentes nomes de campo
  const profileData = {
    name: user?.name || user?.name_aluno || user?.name_professor || "Carregando...",
    email: user?.email || user?.email_aluno || user?.email_professor || "Carregando...",
    cpf: user?.cpf || user?.cpf_aluno || user?.cpf_professor || "Carregando...",
    phone: user?.phone_number || user?.phone_number_aluno || user?.phone_number_professor || "Carregando...",
    birthday: user?.birthday || user?.birthday_aluno || user?.birthday_professor || null
  };

  return (
    // Mantemos a classe original para que as abas funcionem
    <div
      className={`tabs__pane -tab-item-1 ${activeTab == 1 ? "is-active" : ""} `}
    >
      <Paper elevation={0} sx={{ p: { xs: 2, sm: 4 }, mt: 4, border: '1px solid #eee' }}>
        <Typography variant="h5" gutterBottom>
          Minhas Informações
        </Typography>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
            <CircularProgress />
            <Typography sx={{ ml: 2 }}>Carregando perfil...</Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error">{error}</Alert>
        )}

        {!loading && !error && user && (
          <Grid container spacing={3} mt={1}>
            {/* Usamos o componente ProfileField para exibir os dados normalizados */}
            <ProfileField label="Nome Completo" value={profileData.name} />
            <ProfileField label="Email" value={profileData.email} />
            <ProfileField label="CPF" value={profileData.cpf} />
            <ProfileField label="Telefone" value={profileData.phone} />
            <ProfileField label="Data de Nascimento" value={formatDate(profileData.birthday)} />
          </Grid>
        )}
      </Paper>
    </div>
  );
}