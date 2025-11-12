import React, { useState, useEffect } from "react";
import FooterNine from "../layout/footers/FooterNine";
import PageLinksTwo from "../common/PageLinksTwo";
import api from "@/api/axios";
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Box,
  Grid,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Card,
  CardContent,
  Chip,
} from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon
} from "@mui/icons-material";

// Função helper para headers de autenticação
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

// Lista estática de turmas
const TURMAS_ESTATICAS = [
  { value: "1A", label: "1º ANO A" },
  { value: "1B", label: "1º ANO B" },
  { value: "1C", label: "1º ANO C" },
  { value: "2A", label: "2º ANO A" },
  { value: "2B", label: "2º ANO B" },
  { value: "2C", label: "2º ANO C" },
  { value: "3A", label: "3º ANO A" },
  { value: "3B", label: "3º ANO B" },
  { value: "3C", label: "3º ANO C" },
];

// Lista estática de turnos
const TURNOS_ESTATICOS = [
  { value: "MATUTINO", label: "Matutino" },
  { value: "VESPERTINO", label: "Vespertino" },
];

// Lista estática de professores (TEMPORÁRIA - enquanto backend não funciona)
const PROFESSORES_ESTATICOS = [
  { id: 1, name_professor: "Você" },
];

export default function PlanejamentoSemanal() {
  const [planejamentos, setPlanejamentos] = useState([]);
  const [professores, setProfessores] = useState(PROFESSORES_ESTATICOS);
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [editId, setEditId] = useState(null);

  const [form, setForm] = useState({
    professor: "",
    turma: "",
    disciplina: "",
    data_aula: "",
    turno: "",
    conteudo: "",
    atividades: "",
    recursos: "",
    observacoes: ""
  });

  // Carregar dados
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      // Tenta buscar planejamentos, mas usa lista vazia se der erro
      try {
        const planejamentosRes = await api.get("/planejamentos-semanais/", { headers });
        setPlanejamentos(planejamentosRes.data);
      } catch (error) {
        console.log("Não foi possível carregar planejamentos, usando lista vazia");
        setPlanejamentos([]);
      }

    } catch (error) {
      console.error("Erro ao buscar dados:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!form.professor || !form.turma || !form.disciplina || !form.data_aula) {
      alert("Preencha os campos obrigatórios: Professor, Turma, Disciplina e Data da Aula");
      return;
    }

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      console.log("Tentando salvar planejamento...");

      // SOLUÇÃO TEMPORÁRIA: Simular sucesso enquanto backend não funciona
      
      
      // Simular sucesso
      const novoPlanejamento = {
        id: Date.now(),
        ...form,
        professor: professores.find(p => p.id == form.professor) || { name_professor: "Professor" }
      };
      
      if (editId) {
        setPlanejamentos(prev => prev.map(p => p.id === editId ? novoPlanejamento : p));
      } else {
        setPlanejamentos(prev => [...prev, novoPlanejamento]);
      }
      
      resetForm();
      setOpenDialog(false);
      alert(`Planejamento ${editId ? "atualizado" : "criado"} com sucesso! (Dados locais)`);

    } catch (error) {
      console.error("Erro ao salvar:", error.response?.data);

    }
  };

  const resetForm = () => {
    setForm({
      professor: "",
      turma: "",
      disciplina: "",
      data_aula: "",
      turno: "",
      conteudo: "",
      atividades: "",
      recursos: "",
      observacoes: ""
    });
    setEditId(null);
  };

  const handleEdit = (planejamento) => {
    setForm({
      professor: planejamento.professor?.id || planejamento.professor,
      turma: planejamento.turma,
      disciplina: planejamento.disciplina,
      data_aula: planejamento.data_aula,
      turno: planejamento.turno,
      conteudo: planejamento.conteudo,
      atividades: planejamento.atividades,
      recursos: planejamento.recursos,
      observacoes: planejamento.observacoes
    });
    setEditId(planejamento.id);
    setOpenDialog(true);
  };

  const handleDelete = async (id) => {
    if (!confirm("Tem certeza que deseja excluir este planejamento?")) return;
    
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      // SOLUÇÃO TEMPORÁRIA: Remover localmente
      setPlanejamentos(prev => prev.filter(p => p.id !== id));
      alert("Planejamento excluído com sucesso! (Dados locais)");

    } catch (error) {
      console.error("Erro ao excluir:", error);
      alert("Erro ao excluir planejamento.");
    }
  };

  const handleOpenDialog = () => {
    resetForm();
    // ⬇️ LINHA ADICIONADA: Define 'Você' (ID 1) como professor padrão
    setForm(prev => ({ ...prev, professor: 1 }));
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    resetForm();
  };

  // Funções auxiliares
  const getNomeProfessor = (professor) => {
    if (!professor) return "N/A";
    if (typeof professor === 'object') return professor.name_professor;
    const prof = professores.find(p => p.id === professor);
    return prof ? prof.name_professor : `Professor ${professor}`;
  };

  const getLabel = (valor, array) => {
    const item = array?.find(item => item.value === valor);
    return item ? item.label : valor;
  };

  return (
    <div className="dashboard__main">
      <div className="dashboard__content bg-light-4">
        <div className="row pb-50 mb-10">
          <div className="col-auto">
            <h1 className="text-30 lh-12 fw-700">Planejamento Semanal de Aulas</h1>
            <PageLinksTwo />
          </div>
        </div>


        {/* Cards de Estatísticas */}
        <Box sx={{ mb: 4 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={4}>
              <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                    {planejamentos.length}
                  </Typography>
                  <Typography variant="body2">
                    Total de Planejamentos
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ bgcolor: 'warning.main', color: 'white' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                    {new Set(planejamentos.map(p => p.professor)).size}
                  </Typography>
                  <Typography variant="body2">
                    Professores com Planejamento
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ bgcolor: 'success.main', color: 'white' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                    {new Set(planejamentos.map(p => p.turma)).size}
                  </Typography>
                  <Typography variant="body2">
                    Turmas com Planejamento
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>

        {/* Conteúdo Principal */}
        <Card>
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold' }}>
                Planejamentos Cadastrados
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleOpenDialog}
                sx={{ borderRadius: 2 }}
              >
                Novo Planejamento
              </Button>
            </Box>

            {loading && (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography>Carregando...</Typography>
              </Box>
            )}

            <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
              <Table>
                <TableHead sx={{ bgcolor: 'primary.main' }}>
                  <TableRow>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Professor</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Turma</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Disciplina</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Data</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Turno</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }} width="120">Ações</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {planejamentos.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                        <Typography variant="body1" color="textSecondary">
                          Nenhum planejamento cadastrado
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    planejamentos.map(planejamento => (
                      <TableRow key={planejamento.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <PersonIcon fontSize="small" color="action" />
                            <Typography variant="body2">
                              {getNomeProfessor(planejamento.professor)}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={getLabel(planejamento.turma, TURMAS_ESTATICAS)} 
                            size="small" 
                            color="primary" 
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                            {planejamento.disciplina}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {new Date(planejamento.data_aula).toLocaleDateString('pt-BR')}
                        </TableCell>
                        <TableCell>
                          {getLabel(planejamento.turno, TURNOS_ESTATICOS)}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton 
                              size="small" 
                              color="warning"
                              onClick={() => handleEdit(planejamento)}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                            <IconButton 
                              size="small" 
                              color="error"
                              onClick={() => handleDelete(planejamento.id)}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </Card>

        {/* Modal de Formulário */}
        <Dialog 
          open={openDialog} 
          onClose={handleCloseDialog}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
              {editId ? "Editar Planejamento" : "Novo Planejamento Semanal"}
            </Typography>
          </DialogTitle>
          <form onSubmit={handleSubmit}>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    required
                    disabled
                    label="Professor Responsável"
                    value="Você"
                    InputLabelProps={{ shrink: true }} // Garante que o label não sobreponha o valor
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth required>
                    <InputLabel>Turma</InputLabel>
                    <Select
                      name="turma"
                      value={form.turma}
                      onChange={handleChange}
                      label="Turma"
                    >
                      {TURMAS_ESTATICAS.map(turma => (
                        <MenuItem key={turma.value} value={turma.value}>
                          {turma.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    required
                    name="disciplina"
                    label="Disciplina"
                    value={form.disciplina}
                    onChange={handleChange}
                    placeholder="Ex: Matemática, Português..."
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    required
                    type="date"
                    name="data_aula"
                    label="Data da Aula"
                    value={form.data_aula}
                    onChange={handleChange}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Turno</InputLabel>
                    <Select
                      name="turno"
                      value={form.turno}
                      onChange={handleChange}
                      label="Turno"
                    >
                      {TURNOS_ESTATICOS.map(turno => (
                        <MenuItem key={turno.value} value={turno.value}>
                          {turno.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    name="conteudo"
                    label="Conteúdo Programado"
                    value={form.conteudo}
                    onChange={handleChange}
                    placeholder="Descreva o conteúdo que será ministrado..."
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    name="atividades"
                    label="Atividades Previstas"
                    value={form.atividades}
                    onChange={handleChange}
                    placeholder="Descreva as atividades planejadas..."
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    name="recursos"
                    label="Recursos Necessários"
                    value={form.recursos}
                    onChange={handleChange}
                    placeholder="Liste os recursos necessários..."
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    name="observacoes"
                    label="Observações"
                    value={form.observacoes}
                    onChange={handleChange}
                    placeholder="Observações adicionais..."
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions sx={{ p: 3 }}>
              <Button onClick={handleCloseDialog} color="inherit">
                Cancelar
              </Button>
              <Button 
                type="submit" 
                variant="contained"
                disabled={!form.professor || !form.turma || !form.disciplina || !form.data_aula}
              >
                {editId ? "Atualizar" : "Salvar"} Planejamento
              </Button>
            </DialogActions>
          </form>
        </Dialog>
      </div>

      <FooterNine />
    </div>
  );
}