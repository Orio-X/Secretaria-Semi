// EM: src/components/dashboard/ReservaSalas.jsx 

import React, { useState, useEffect } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Grid, Typography, FormControl, InputLabel, Select, MenuItem, TextField } from "@mui/material";
import FooterNine from "../layout/footers/FooterNine";
import PageLinksTwo from "../common/PageLinksTwo";
import api from "@/api/axios";

// -----------------------------------------------------------------
// FUNÇÕES HELPER (Para autossuficiência do componente)
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

// Definindo os Choices de Tipo de Sala (baseado no models.py)
const TIPO_CHOICES_RESERVA = [
    { value: '', label: 'Qualquer Tipo' },
    { value: 'SALA', label: 'Sala de Aula' },
    { value: 'LAB', label: 'Laboratório' },
    { value: 'QUADRA', label: 'Quadra/Esporte' },
];

// -----------------------------------------------------------------
// 1. MODAL DE FORMULÁRIO DE RESERVA
// -----------------------------------------------------------------
function ReservaFormModal({ open, onClose, onSubmit, salas = [], userProfessorId }) {
    const [selectedTipo, setSelectedTipo] = useState(''); 
    const [submissionError, setSubmissionError] = useState(null);
    
    const initialForm = {
        professor: userProfessorId,
        sala: null,
        data: new Date().toISOString().split('T')[0],
        horario_inicio: '08:00', 
        horario_fim: '09:00', 
        finalidade: '',
    };
    const [form, setForm] = useState(initialForm);

    // Efeito para resetar o form quando abrir o modal
    useEffect(() => {
        if (open) {
            setForm(initialForm);
            setSelectedTipo('');
            setSubmissionError(null);
        }
    }, [open]);

    // DEBUG: Verifique os dados recebidos
    console.log("Salas recebidas no modal:", salas);
    console.log("User Professor ID:", userProfessorId);

    // FILTRAGEM: Gera a lista de salas filtradas em tempo real
    const salasFiltradas = salas.filter(s => {
        if (!s || !s.tipo) return false;
        return selectedTipo === '' || s.tipo === selectedTipo;
    });

    console.log("Tipo selecionado:", selectedTipo);
    console.log("Salas filtradas:", salasFiltradas);

    // Função para obter o display name da sala
    const getSalaDisplayName = (sala) => {
        if (!sala) return '';
        
        const tipoDisplay = sala.tipo_display || 
                           (sala.tipo === 'SALA' ? 'Sala de Aula' :
                            sala.tipo === 'LAB' ? 'Laboratório' :
                            sala.tipo === 'QUADRA' ? 'Quadra/Esporte' : sala.tipo);
        
        return `${sala.nome || 'Sem nome'} (${tipoDisplay})`;
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        
        // LÓGICA DE FILTRO: Se o tipo mudar, resetar a sala selecionada
        if (name === 'tipo_filtro') {
            setSelectedTipo(value);
            setForm(prev => ({ ...prev, sala: null })); // Resetar a sala
            return;
        }

        // Lógica para campos normais
        const finalValue = name === 'sala' ? (value === '' ? null : Number(value)) : value;
        setForm(prev => ({ ...prev, [name]: finalValue }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setSubmissionError(null);
        
        // Validação básica do Front-end
        if (!form.sala) {
            setSubmissionError("Selecione uma sala válida.");
            return;
        }
        
        // Validação de horário
        if (form.horario_inicio >= form.horario_fim) {
            setSubmissionError("O horário de início deve ser anterior ao horário de fim.");
            return;
        }
        
        onSubmit(form, setSubmissionError); 
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>Reservar Sala/Laboratório</DialogTitle>
            <form onSubmit={handleSubmit}>
                <DialogContent>
                    <Grid container spacing={2} mt={1}>
                        {/* CAMPO DE FILTRO POR TIPO */}
                        <Grid item xs={12}>
                            <FormControl fullWidth size="small">
                                <InputLabel>Filtrar Tipo de Sala</InputLabel>
                                <Select 
                                    name="tipo_filtro" 
                                    label="Filtrar Tipo de Sala" 
                                    value={selectedTipo} 
                                    onChange={handleChange}
                                >
                                    {TIPO_CHOICES_RESERVA.map(t => (
                                        <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>
                        
                        {/* CAMPO DE SELEÇÃO DE SALA (FILTRADO) */}
                        <Grid item xs={12}>
                            <FormControl 
                                fullWidth 
                                required 
                                size="small" 
                                error={salasFiltradas.length === 0}
                                disabled={salasFiltradas.length === 0}
                            >
                                <InputLabel>Sala</InputLabel>
                                <Select 
                                    name="sala" 
                                    label="Sala" 
                                    value={form.sala || ""} 
                                    onChange={handleChange}
                                >
                                    <MenuItem value=""><em>Selecione a Sala</em></MenuItem>
                                    {salasFiltradas.map(s => (
                                        <MenuItem key={s.id} value={s.id}>
                                            {getSalaDisplayName(s)}
                                        </MenuItem>
                                    ))}
                                </Select>
                                {salasFiltradas.length === 0 && (
                                    <Typography variant="caption" color="error">
                                        Nenhuma sala disponível para o tipo selecionado.
                                    </Typography>
                                )}
                            </FormControl>
                        </Grid>

                        {/* BLOCO DE EXIBIÇÃO DE ERRO CENTRALIZADO */}
                        {submissionError && (
                            <Grid item xs={12}>
                                <Typography color="error" variant="body2" sx={{ p: 1, border: '1px solid red', borderRadius: 1 }}>
                                    🚨 Erro de Reserva: {submissionError}
                                </Typography>
                            </Grid>
                        )}
                        
                        <Grid item xs={12}>
                            <TextField 
                                name="data" 
                                label="Data da Reserva" 
                                type="date" 
                                value={form.data} 
                                onChange={handleChange} 
                                fullWidth 
                                required 
                                size="small" 
                                InputLabelProps={{ shrink: true }} 
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField 
                                name="horario_inicio" 
                                label="Início" 
                                type="time" 
                                value={form.horario_inicio} 
                                onChange={handleChange} 
                                fullWidth 
                                required 
                                size="small" 
                                InputLabelProps={{ shrink: true }} 
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField 
                                name="horario_fim" 
                                label="Fim" 
                                type="time" 
                                value={form.horario_fim} 
                                onChange={handleChange} 
                                fullWidth 
                                required 
                                size="small" 
                                InputLabelProps={{ shrink: true }} 
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField 
                                name="finalidade" 
                                label="Finalidade" 
                                value={form.finalidade} 
                                onChange={handleChange} 
                                fullWidth 
                                required 
                                multiline 
                                rows={2} 
                                size="small" 
                            />
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={onClose}>Cancelar</Button>
                    <Button type="submit" variant="contained">Reservar</Button>
                </DialogActions>
            </form>
        </Dialog>
    );
}

// -----------------------------------------------------------------
// 2. COMPONENTE PRINCIPAL (Visualização do Professor)
// -----------------------------------------------------------------
export default function ReservaSalas() {
    const [minhasReservas, setMinhasReservas] = useState([]);
    const [salas, setSalas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modalOpen, setModalOpen] = useState(false);
    
    // LÓGICA DE PROFESSOR ID: PRECISA SER INTEGRADA COM SEU CONTEXTO/TOKEN
    const userProfessorId = 1; // Temporário - ajuste conforme sua autenticação

    const fetchData = async () => {
        setLoading(true);
        const headers = getAuthHeaders();
        if (!headers) { 
            console.error("Headers de autenticação não disponíveis");
            setLoading(false); 
            return; 
        }
        
        try {
            console.log("Buscando dados da API...");
            
            // CORREÇÃO: URLs corrigidas
            const [reservasRes, salasRes] = await Promise.allSettled([
                api.get(`/reservas/?professor=${userProfessorId}`, { headers }),
                api.get("/salas/", { headers }),
            ]);

            console.log("Resposta reservas:", reservasRes);
            console.log("Resposta salas:", salasRes);

            // CORREÇÃO: Tratamento das respostas
            if (reservasRes.status === 'fulfilled') {
                const reservasData = reservasRes.value.data.results || reservasRes.value.data || [];
                console.log("Reservas carregadas:", reservasData);
                setMinhasReservas(reservasData);
            } else {
                console.error("Erro ao buscar reservas:", reservasRes.reason);
                setMinhasReservas([]);
            }

            if (salasRes.status === 'fulfilled') {
                const salasData = salasRes.value.data.results || salasRes.value.data || [];
                console.log("Salas carregadas:", salasData);
                setSalas(salasData);
            } else {
                console.error("Erro ao buscar salas:", salasRes.reason);
                setSalas([]);
            }

        } catch (error) { 
            console.error("Erro geral ao buscar dados:", error); 
        } 
        finally { 
            setLoading(false); 
        }
    };
    
    useEffect(() => { 
        fetchData(); 
    }, []);

    const handleOpenModal = () => setModalOpen(true);
    const handleCloseModal = () => { 
        setModalOpen(false); 
        fetchData(); // Recarregar dados após fechar modal
    };
    
    // TRATAMENTO DE ERRO NO COMPONENTE PAI
    const handleFormSubmit = async (formData, setSubmissionError) => {
        const headers = getAuthHeaders();
        if (!headers) {
            setSubmissionError("Erro de autenticação. Faça login novamente.");
            return;
        }

        try {
            console.log("Enviando dados da reserva:", formData);
            
            const response = await api.post("/reservas/", formData, { headers });
            console.log("Reserva criada com sucesso:", response.data);
            
            window.alert("Sala reservada com sucesso!"); 
            handleCloseModal();
        } catch (error) {
            console.error("Erro ao criar reserva:", error);
            console.error("Detalhes do erro:", error.response?.data);
            
            let errorMessage = "Erro desconhecido ao processar reserva.";
            
            if (error.response && error.response.data) {
                const errorData = error.response.data;
                
                // 1. Conflito de Horário/Unicidade (non_field_errors)
                if (errorData.non_field_errors && errorData.non_field_errors.length > 0) {
                    errorMessage = errorData.non_field_errors[0]; 
                }
                // 2. Erro em campo específico (Ex: horario_fim)
                else if (errorData.horario_fim) {
                    errorMessage = `Horário Inválido: ${Array.isArray(errorData.horario_fim) ? errorData.horario_fim[0] : errorData.horario_fim}`;
                }
                // 3. Erro de sala
                else if (errorData.sala) {
                    errorMessage = `Sala: ${Array.isArray(errorData.sala) ? errorData.sala[0] : errorData.sala}`;
                }
                // 4. Outros erros
                else {
                    errorMessage = `Erro de Validação: ${JSON.stringify(errorData)}`;
                }
            } else if (error.request) {
                errorMessage = "Erro de conexão com o servidor. Verifique sua internet.";
            }
            
            setSubmissionError(errorMessage);
        }
    };
    
    const handleDelete = async (id) => {
        if (!window.confirm("Confirmar cancelamento da reserva?")) return;
        
        const headers = getAuthHeaders();
        if (!headers) {
            alert("Erro de autenticação.");
            return;
        }

        try {
            await api.delete(`/reservas/${id}/`, { headers });
            alert("Reserva cancelada com sucesso.");
            fetchData(); // Recarregar a lista
        } catch (error) {
            console.error("Erro ao cancelar reserva:", error);
            alert("Erro ao cancelar reserva. Tente novamente.");
        }
    };

    const getSalaNome = (salaId) => {
        const salaObj = salas.find(s => s.id === salaId);
        return salaObj ? salaObj.nome : `Sala ID: ${salaId}`;
    };

    return (
        <div className="dashboard__main">
            <div className="dashboard__content bg-light-4">
                <div className="row pb-50 mb-10">
                    <div className="col-auto">
                        <h1 className="text-30 lh-12 fw-700">Reserva de Salas</h1>
                        <PageLinksTwo />
                    </div>
                </div>

                <div className="row y-gap-30">
                    <div className="col-12">
                        <div className="rounded-16 bg-white shadow-4 h-100">
                            <div className="d-flex justify-between items-center py-20 px-30 border-bottom-light">
                                <h2 className="text-17 lh-1 fw-500">Minhas Reservas</h2>
                                <Button variant="contained" color="primary" onClick={handleOpenModal}>
                                    Nova Reserva
                                </Button>
                            </div>

                            <div className="py-30 px-30">
                                {/* TABELA DE MINHAS RESERVAS */}
                                <Box>
                                    <table className="table table-bordered">
                                        <thead>
                                            <tr>
                                                <th>Sala</th>
                                                <th>Data</th>
                                                <th>Início</th>
                                                <th>Fim</th>
                                                <th>Finalidade</th>
                                                <th>Ações</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {loading ? (
                                                <tr>
                                                    <td colSpan="6" className="text-center">Carregando reservas...</td>
                                                </tr>
                                            ) : minhasReservas.length > 0 ? (
                                                minhasReservas.map(reserva => (
                                                    <tr key={reserva.id}>
                                                        <td>{getSalaNome(reserva.sala)}</td>
                                                        <td>{new Date(reserva.data).toLocaleDateString('pt-BR')}</td>
                                                        <td>{reserva.horario_inicio}</td>
                                                        <td>{reserva.horario_fim}</td>
                                                        <td>{reserva.finalidade}</td>
                                                        <td>
                                                            <button 
                                                                className="btn btn-sm btn-danger" 
                                                                onClick={() => handleDelete(reserva.id)}
                                                            >
                                                                Cancelar
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))
                                            ) : (
                                                <tr>
                                                    <td colSpan="6" className="text-center">
                                                        Nenhuma reserva agendada.
                                                    </td>
                                                </tr>
                                            )}
                                        </tbody>
                                    </table>
                                </Box>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <FooterNine />
            
            <ReservaFormModal 
                open={modalOpen} 
                onClose={handleCloseModal} 
                onSubmit={handleFormSubmit} 
                salas={salas}
                userProfessorId={userProfessorId}
            />
        </div>
    );
}