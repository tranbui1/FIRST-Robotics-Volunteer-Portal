import { useNavigate } from 'react-router-dom';

/**
 * Modal
 * 
 * Confirmation modal for exiting the questionnaire. Warns the user that
 * progress will not be saved and provides options to cancel or exit.
 * 
 * Props:
 *  - setModalOpen: function — Callback to update modal visibility state.
 * 
 * Usage:
 *  <Modal setModalOpen={setModalOpen} />
 */
const Modal = ({ setModalOpen }) => {
    let navigate = useNavigate();

    return (
        <div className="modal-overlay">
            <div className="modal-content"> 
                <p className="modal-header"> Exit Questionnaire? </p>
                <p className="modal-text"> Are you sure you want to exit this quiz? <br /> Your progress will not
                    be saved.
                </p>
                <div className="modal-buttons"> 
                    <button className="button gray" onClick={() => setModalOpen(false)}> Cancel </button>
                    <button className="button red" onClick={() => navigate('/')}> Exit </button>
                </div>
            </div>
        </div>
    )
}

export default Modal;
