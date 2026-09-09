import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useLocation, useNavigate } from "react-router-dom";
import { z } from "zod";
import { useAuth } from "../../contexts/AuthContext";

const schema = z.object({
  login_ou_email: z.string().min(3, "Informe seu login ou e-mail"),
  senha: z.string().min(1, "Informe a senha"),
});

type FormValues = z.infer<typeof schema>;

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [erro, setErro] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const destino = (location.state as { from?: string } | null)?.from ?? "/admin/dashboard";

  async function onSubmit(values: FormValues) {
    setErro(null);
    try {
      await login(values.login_ou_email, values.senha);
      navigate(destino, { replace: true });
    } catch {
      setErro("Login/e-mail ou senha inválidos");
    }
  }

  return (
    <div className="form-container" style={{ maxWidth: 360 }}>
      <h1>Login administrativo</h1>

      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <div className="form-field">
          <label htmlFor="login_ou_email">Login ou e-mail</label>
          <input id="login_ou_email" {...register("login_ou_email")} />
          {errors.login_ou_email && (
            <span className="form-error">{errors.login_ou_email.message}</span>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="senha">Senha</label>
          <input id="senha" type="password" {...register("senha")} />
          {errors.senha && <span className="form-error">{errors.senha.message}</span>}
        </div>

        {erro && <div className="form-error form-error-geral">{erro}</div>}

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
