export default function Error(props: any) {
    return (
      <div id="error">
        <h3>ERROR!</h3>
        <h3>Se ha producido un error</h3>
        <p>Código de error: {props.error?.cod}</p>
        <p>Descripción del error: {props.error?.message}</p>
      </div>
    );
  }