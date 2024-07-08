import Input from "../../components/UI/Input";
import { RiProfileLine } from "react-icons/ri";
import { TfiEmail } from "react-icons/tfi";
import { BsCardText } from "react-icons/bs";
import { useState } from "react";
import { Spinner } from "reactstrap";
import { useForm } from "react-hook-form";
import gradientbg from "../../assets/images/banner/vector2.png";
import Cookies from 'js-cookie'; 
import { Form, Button ,notification} from 'antd';
import { BASE_URL } from "../../utils/config";


const AskQuestion = () => {
  const [isLoading, setIsLoading] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();
  
  const onSubmit = async (formData) => {
    try {
      setIsLoading(true);

      const client_id = Cookies.get('userid');

      const response = await fetch(`${BASE_URL}/faqs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: client_id || '',
          name: formData.name,
          contact: formData.emailOrPhone,
          question: formData.questionText
        })
      });

      const data = await response.json();

      if (response.ok) {
        notification.success({
          message: 'Success',
          description: 'Your message has been submitted successfully!'
        });
        setIsLoading(false);
      } else {
        notification.error({
          message: 'Error',
          description: 'Failed to submit your message. Please try again later.'
        });
        setIsLoading(false);
      }
    } catch (error) {
      notification.error({
        message: 'Error',
        description: 'An error occurred while submitting your message. Please try again later.'
      });
      setIsLoading(false);
    }
  };

  return (
    <div className="lg:max-w-[500px] w-full px-5 py-6 backdrop-blur-md rounded-xl border-3 ">
      <div className="mb-4 text-white">
        <h3 className="text-black leading-tight">
          Any Question?
        </h3>
        <h3 className="text-black text-[20px]">
          Don&apos;t worry, we can help.
        </h3>
      </div>

      <div>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="font-brand__font__semibold text-black">
            <div className="relative text-gray-600">
              <input
                name="name"
                type="text"
                placeholder="Your name"
                className="w-full rounded py-3 pl-4 pr-9 border-2 outline-none mb-2 placeholder:text-brand__font__size__sm"
                {...register("name", {
                  required: true,
                })}
              />

              <RiProfileLine className="absolute top-3 right-2" size={20} />
            </div>
            <div className="relative text-gray-600">
              <input
                name="emailOrPhone"
                type="text"
                placeholder="Your phone or email"
                className="w-full rounded py-3 pl-4 pr-9 border-2 outline-none mb-2 placeholder:text-brand__font__size__sm"
                {...register("emailOrPhone", {
                  required: true,
                })}
              />
              <TfiEmail className="absolute top-3 right-2" size={18} />
            </div>

            <div className="relative text-gray-600">
              <textarea
                name="questionText"
                type="text"
                rows="6"
                placeholder="Please write your question"
                className="w-full rounded py-3 pl-4 pr-9 border-2 outline-none mb-2 placeholder:text-brand__font__size__sm resize-none"
                {...register("questionText", {
                  required: true,
                })}
              />
              <BsCardText className="absolute top-3 right-2" size={20} />
            </div>

            {isLoading ? (
              <div className="w-full flex justify-center">
                <Spinner styles="w-6 h-6 border-white mx-auto" />
              </div>
            ) : (
              <Input
                type="submit"
                value="Submit"
                className="w-full rounded bg-black text-white p-2 cursor-pointer hover:bg-primary duration-300 text-brand__font__size__md"
              />
            )}
          </div>
        </form>
      </div>
      
    </div>
  );
};

export default AskQuestion;
