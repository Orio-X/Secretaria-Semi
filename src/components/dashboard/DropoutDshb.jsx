import React, { useState, useEffect, useCallback } from "react";
import FooterNine from "../layout/footers/FooterNine";
import api from "@/api/axios";

// --- [NOVO] IMPORTS DO MATERIAL-UI (Para o filtro profissional) ---
import {
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box 
} from "@mui/material";

// -----------------------------------------------------------------
// FUNÇÃO HELPER PARA PEGAR OS HEADERS DE AUTENTICAÇÃO
// -----------------------------------------------------------------
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

// -----------------------------------------------------------------
// FUNÇÃO HELPER PARA PEGAR O NOME FORMATADO
// -----------------------------------------------------------------
const getNomeFormatado = (aluno) => {
    if (aluno.name_aluno) return aluno.name_aluno;
    if (aluno.nome) return aluno.nome;
    const primeiro = aluno.first_name || aluno.primeiro_nome;
    const ultimo = aluno.last_name || aluno.ultimo_nome;
    if (primeiro) {
        return `${primeiro} ${ultimo || ''}`.trim();
    }
    return 'Nome Indisponível';
};

// -----------------------------------------------------------------
// COMPONENTE DE CARD DE ESTATÍSTICA (Para os 3 cards)
// -----------------------------------------------------------------
const StatCard = ({ title, value, icon, colorClass = 'text-dark-1', loading }) => {
    if (loading) {
        return (
            <div className="col-xl-4 col-md-6">
                <div className="py-35 px-30 bg-white shadow-4 rounded-16">Carregando...</div>
            </div>
        );
    }
    
    return (
        <div className="col-xl-4 col-md-6">
            <div className="d-flex justify-between items-center py-35 px-30 rounded-16 bg-white -dark-bg-dark-1 shadow-4">
                <div>
                    <div className="lh-1 fw-500">{title}</div>
                    <div className={`text-32 lh-1 fw-700 mt-20 ${colorClass}`}>
                        {value}
                    </div>
                </div>
                <i className={`text-40 ${icon} ${colorClass}`}></i>
            </div>
        </div>
    );
};

// -----------------------------------------------------------------
// --- [NOVO] COMPONENTE TURMASELECT (IDÊNTICO AO SEU ADMINISTRATION.JSX) ---
// -----------------------------------------------------------------
const TurmaSelect = ({ value, onChange, name = "class_choice", label = "Turma", ...props }) => (
    <FormControl fullWidth {...props} size="small">
        <InputLabel>{label}</InputLabel>
        <Select name={name} value={value} label={label} onChange={onChange}>
            <MenuItem value=""><em>{label}</em></MenuItem>
            {/* Lista estática baseada no seu models.py (TURMA_CHOICES) */}
            <MenuItem value="1A">1 ANO A</MenuItem>
            <MenuItem value="1B">1 ANO B</MenuItem>
            <MenuItem value="1C">1 ANO C</MenuItem>
            <MenuItem value="2A">2 ANO A</MenuItem>
            <MenuItem value="2B">2 ANO B</MenuItem>
            <MenuItem value="2C">2 ANO C</MenuItem>
            <MenuItem value="3A">3 ANO A</MenuItem>
            <MenuItem value="3B">3 ANO B</MenuItem>
            <MenuItem value="3C">3 ANO C</MenuItem>
        </Select>
    </FormControl>
);


// =================================================================
// --- COMPONENTE PRINCIPAL: DropoutDshb ---
// =================================================================
export default function DropoutDshb() {
    // --- ESTADOS GLOBAIS DE DADOS E STATUS ---
    const [alunos, setAlunos] = useState([]);
    const [totalAlunos, setTotalAlunos] = useState(0);
    const [ativos, setAtivos] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [updatingId, setUpdatingId] = useState(null); 

    // --- [MODIFICADO] ESTADO DE FILTRO (padrão AlunoAdminPanel) ---
    const [filters, setFilters] = useState({ nome: "", cpf: "", turma: "" });

    // -----------------------------------------------------------------
    // LÓGICA DE BUSCA DE DADOS
    // -----------------------------------------------------------------
    const fetchAlunos = useCallback(async () => {
        setLoading(true);
        setError(null);
        const headers = getAuthHeaders();
        if (!headers) {
            setLoading(false);
            setError("Token ausente. Faça login novamente.");
            return;
        }

        try {
            const res = await api.get("/alunos/", { headers });
            const alunosData = Array.isArray(res.data) ? res.data : res.data.results || [];
            
            const total = alunosData.length;
            const ativosCount = alunosData.filter(a => a.ativo).length; 

            setAlunos(alunosData);
            setTotalAlunos(total);
            setAtivos(ativosCount);

        } catch (err) {
            console.error("Erro ao buscar dados de alunos:", err.response?.data || err);
            setError("Falha ao carregar dados. (Verifique o console para detalhes)");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchAlunos();
    }, [fetchAlunos]);
    
    // --- CÁLCULOS DERIVADOS ---
    const evadidos = totalAlunos - ativos;
    const taxaEvasao = totalAlunos > 0 ? ((evadidos / totalAlunos) * 100).toFixed(2) : '0.00';


    // --- HANDLER DE FILTRO (padrão AlunoAdminPanel) ---
    const handleFilterChange = (e) => {
        setFilters(prev => ({ ...prev, [e.target.name]: e.target.value }));
    };

    // --- [MODIFICADO] ALUNOS FILTRADOS (usa os 3 filtros) ---
    const filteredAlunos = alunos.filter(aluno =>
        (getNomeFormatado(aluno).toLowerCase().includes(filters.nome.toLowerCase())) &&
        // Usando os nomes dos campos do seu models.py
        (aluno.cpf_aluno?.includes(filters.cpf)) &&
        (filters.turma === "" || aluno.class_choice === filters.turma)
    );

    // -----------------------------------------------------------------
    // LÓGICA DE ATUALIZAÇÃO (com lógica de reverter)
    // -----------------------------------------------------------------
    const handleToggleAtivo = async (aluno) => {
        const novoStatus = !aluno.ativo; 
        const nomeAluno = getNomeFormatado(aluno);
        const acao = novoStatus ? "ATIVO" : "EVADIDO";

        // Validação (seu código original)
        if (aluno.Responsavel === undefined || aluno.Responsavel === null) {
            console.error(`O objeto 'aluno' (ID: ${aluno.id}, Nome: ${nomeAluno}) está sem o campo 'Responsavel'. O PATCH (atualização) provavelmente falhará.`);
            alert(`Erro Crítico: O campo 'Responsavel' não foi encontrado para ${nomeAluno}. A API não permite esta atualização. (Verifique o console)`);
            return;
        }

        const confirmacao = window.confirm(`Tem certeza que deseja marcar ${nomeAluno} como ${acao}?`);
        if (!confirmacao) return;

        setUpdatingId(aluno.id);
        const headers = getAuthHeaders();
        
        // O payload precisa do Responsavel (baseado no seu código)
        const payload = {
            Responsavel: aluno.Responsavel, 
            ativo: novoStatus                
        };

        try {
            await api.patch(`/alunos/${aluno.id}/`, payload, { headers });
            alert(`${nomeAluno} foi marcado como ${acao} com sucesso!`);
            fetchAlunos(); // Recarrega os dados

        } catch (err) {
            console.error(`Erro ao marcar ${nomeAluno} como ${acao}:`, err.response?.data || err);
            const apiError = err.response?.data?.Responsavel || err.response?.data?.detail || "A API rejeitou a atualização.";
            alert(`Erro ao atualizar ${nomeAluno}: ${apiError}`);
        } finally {
            setUpdatingId(null);
        }
    };

    // -----------------------------------------------------------------
    // RENDERIZAÇÃO PRINCIPAL
    // -----------------------------------------------------------------
    return (
        <div className="dashboard__main">
            <div className="dashboard__content bg-light-4">
                <div className="row pb-50 mb-10">
                    <div className="col-auto">
                        <h1 className="text-30 lh-12 fw-700">Painel de Controle de Evasão</h1>
                        <div className="mt-10">
                            Monitore o status dos alunos e registre as saídas.
                        </div>
                    </div>
                </div>

                {/* [MODIFICADO] CARDS DE RESUMO (AGORA 3 CARDS) */}
                <div className="row y-gap-30">
                    {error ? (
                        <div className="col-12">
                            <div className="py-35 px-30 bg-red-1 shadow-4 rounded-16 text-white">{error}</div>
                        </div>
                    ) : (
                        <>
                            <StatCard 
                                title="Taxa de Evasão" 
                                value={`${taxaEvasao}%`} 
                                icon="icon-percent"
                                colorClass={taxaEvasao > 0 ? 'text-red-1' : 'text-dark-1'}
                                loading={loading}
                            />
                            <StatCard 
                                title="Alunos Ativos" 
                                value={ativos} 
                                icon="icon-user-check"
                                colorClass="text-green-1"
                                loading={loading}
                            />
                            <StatCard 
                                title="Alunos Evadidos" 
                                value={evadidos} 
                                icon="icon-user-x"
                                colorClass="text-red-1"
                                loading={loading}
                            />
                        </>
                    )}
                </div>
                
                {/* TABELA DE ALUNOS */}
                <div className="row y-gap-30 pt-30">
                    <div className="col-12">
                        <div className="rounded-16 bg-white -dark-bg-dark-1 shadow-4 h-100 p-30">
                            
                            {/* [CORREÇÃO DE COR] Título da tabela (removido text-green-1) */}
                            <h2 className="text-17 lh-1 fw-500 mb-20">
                                Gerenciamento de Status de Alunos
                            </h2>

                            {/* [MODIFICADO] CAMPO DE FILTRO (Estilo MUI do AlunoAdminPanel) */}
                            <Box mb={3}>
                                <Grid container spacing={2}>
                                    <Grid item xs={12} sm={4}>
                                        <TextField 
                                            fullWidth 
                                            label="Filtrar por Nome" 
                                            name="nome" 
                                            value={filters.nome} 
                                            onChange={handleFilterChange} 
                                            variant="outlined" 
                                            size="small" 
                                            disabled={loading}
                                        />
                                    </Grid>
                                    <Grid item xs={12} sm={4}>
                                        <TextField 
                                            fullWidth 
                                            label="Filtrar por CPF" 
                                            name="cpf" 
                                            value={filters.cpf} 
                                            onChange={handleFilterChange} 
                                            variant="outlined" 
                                            size="small" 
                                            disabled={loading}
                                        />
                                    </Grid>
                                    <Grid item xs={12} sm={4}>
                                        {/* Este é o seu TurmaSelect estático */}
                                        <TurmaSelect 
                                            value={filters.turma} 
                                            onChange={handleFilterChange} 
                                            name="turma" 
                                            label="Filtrar por Turma" 
                                            disabled={loading}
                                            fullWidth 
                                        />
                                    </Grid>
                                </Grid>
                            </Box>

                            {/* Indicadores de Loading/Erro */}
                            {loading && !alunos.length && <div className="text-center py-50">Carregando lista de alunos...</div>}
                            {error && !loading && <div className="text-red-1">Não foi possível carregar a lista.</div>}

                            {!loading && !error && (
                                <div className="dashboard-table">
                                    
                                    {/* [MODIFICADO] Cabeçalho da Tabela (AGORA COM 5 COLUNAS) */}
                                    <div className="d-flex items-center text-15 fw-500 text-dark-1 bg-light-3 rounded-8 px-20 py-15 mb-10">
                                        <div style={{ width: '30%' }}>Nome do Aluno</div>
                                        <div style={{ width: '20%' }}>CPF</div>
                                        <div style={{ width: '15%' }}>Turma</div>
                                        <div style={{ width: '15%' }}>Status</div>
                                        <div style={{ width: '20%' }}>Ações</div>
                                    </div>

                                    {/* [MODIFICADO] Corpo da Tabela usa 'filteredAlunos' */}
                                    {filteredAlunos.length === 0 ? (
                                        <div className="text-center py-30">
                                            Nenhum aluno encontrado {filters.nome || filters.cpf || filters.turma ? 'com esses filtros.' : '.'}
                                        </div>
                                    ) : (
                                        filteredAlunos.map((aluno) => {
                                            
                                            const nomeDisplay = getNomeFormatado(aluno); 
                                            const isUpdating = updatingId === aluno.id;
                                            
                                            return (
                                                // [MODIFICADO] Corpo da Tabela (AGORA COM 5 COLUNAS)
                                                <div key={aluno.id} className="d-flex items-center border-bottom-light px-20 py-15">
                                                    {/* NOME DO ALUNO */}
                                                    <div style={{ width: '30%' }}>{nomeDisplay}</div>
                                                    
                                                    {/* [NOVO] CPF */}
                                                    <div style={{ width: '20%' }}>
                                                        {aluno.cpf_aluno || 'N/D'}
                                                    </div>

                                                    {/* [NOVO] TURMA */}
                                                    <div style={{ width: '15%' }}>
                                                        {aluno.class_choice || 'N/D'}
                                                    </div>
                                                    
                                                    {/* STATUS */}
                                                    <div style={{ width: '15%' }}>
                                                        <span className={`status-tag fw-500 ${aluno.ativo ? 'text-green-1' : 'text-red-1'}`}>
                                                            {aluno.ativo ? 'Ativo' : 'Evadido'}
                                                        </span>
                                                    </div>
                                                    
                                                    {/* BOTÃO DE AÇÃO */}
                                                    <div style={{ width: '20%' }}>
                                                        <button
                                                            onClick={() => handleToggleAtivo(aluno)} 
                                                            className={`button -sm ${aluno.ativo ? '-red-3' : '-green-3'} text-white-1`}
                                                            disabled={isUpdating || loading}
                                                            style={
                                                                aluno.ativo 
                                                                    ? { color: 'white' } // Botão "Evadido" (Vermelho): Só texto branco
                                                                    : { color: 'white', backgroundColor: '#32c732ff' } // Botão "Ativo" (Verde): Texto branco E fundo verde
                                                            }
                                                        >
                                                            {isUpdating ? 'Atualizando...' : (aluno.ativo ? 'Marcar como Evadido' : 'Marcar como Ativo')}
                                                        </button>
                                                    </div>
                                                </div>
                                            );
                                        })
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <FooterNine />
        </div>
    );
}