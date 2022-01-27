#include "stdlib.h"
#include "stdio.h"
#include <windows.h>
#include <conio.h>
#include <errno.h>
#include <WinDef.h>

#include "../../include/msp_cmn.h"
#include "../../include/qivw.h"
#include "../../include/msp_errors.h"

#pragma comment(lib, "winmm.lib")  

 #ifdef _WIN64
 #pragma comment(lib,"../../libs/msc_x64.lib")
 #else
 #pragma comment(lib, "../../libs/msc.lib")
 #endif

//��ȡ�ļ�
#define IVW_AUDIO_FILE_NAME "audio/awake.pcm"
#define FRAME_LEN	640 //16k�����ʵ�16bit��Ƶ��һ֡�Ĵ�СΪ640B, ʱ��20ms

int wakeupFlage = 0;
void sleep_ms(int ms)
{
	Sleep(ms);
}

int cb_ivw_msg_proc( const char *sessionID, int msg, int param1, int param2, const void *info, void *userData )
{
	if (MSP_IVW_MSG_ERROR == msg) //���ѳ�����Ϣ
	{
		printf("\n\nMSP_IVW_MSG_ERROR errCode = %d\n\n", param1);
	}
	else if (MSP_IVW_MSG_WAKEUP == msg) //���ѳɹ���Ϣ
	{
		printf("\n\nMSP_IVW_MSG_WAKEUP result = %s\n\n", info);
		wakeupFlage = 1;
	}
	return 0;
}
//ͨ����ȡ��Ƶ�ļ����ѵ�demo
void run_ivw(const char *grammar_list, const char* audio_filename ,  const char* session_begin_params)
{
	const char *session_id = NULL;
	int err_code = MSP_SUCCESS;
	FILE *f_aud = NULL;
	long audio_size = 0;
	long real_read = 0;
	long audio_count = 0;
	int count = 0;
	int audio_stat = MSP_AUDIO_SAMPLE_CONTINUE;
	char *audio_buffer=NULL;
	char sse_hints[128];
	if (NULL == audio_filename)
	{
		printf("params error\n");
		return;
	}

	f_aud=fopen(audio_filename, "rb");
	if (NULL == f_aud)
	{
		printf("audio file open failed! \n\n");
		return;
	}
	fseek(f_aud, 0, SEEK_END);
	audio_size = ftell(f_aud);
	fseek(f_aud, 0, SEEK_SET);
	audio_buffer = (char *)malloc(audio_size);
	if (NULL == audio_buffer)
	{
		printf("malloc failed! \n");
		goto exit;
	}
	real_read = fread((void *)audio_buffer, 1, audio_size, f_aud);
	if (real_read != audio_size)
	{
		printf("read audio file failed!\n");
		goto exit;
	}

	session_id=QIVWSessionBegin(grammar_list, session_begin_params, &err_code);
	if (err_code != MSP_SUCCESS)
	{
		printf("QIVWSessionBegin failed! error code:%d\n",err_code);
		goto exit;
	}

	err_code = QIVWRegisterNotify(session_id, cb_ivw_msg_proc,NULL);
	if (err_code != MSP_SUCCESS)
	{
		_snprintf(sse_hints, sizeof(sse_hints), "QIVWRegisterNotify errorCode=%d", err_code);
		printf("QIVWRegisterNotify failed! error code:%d\n",err_code);
		goto exit;
	}
	while(1)
	{
		long len = 10*FRAME_LEN; //16k��Ƶ��10֡ ��ʱ��200ms��
		audio_stat = MSP_AUDIO_SAMPLE_CONTINUE;
		if(audio_size <= len)
		{
			len = audio_size;
			audio_stat = MSP_AUDIO_SAMPLE_LAST; //���һ��
		}
		if (0 == audio_count)
		{
			audio_stat = MSP_AUDIO_SAMPLE_FIRST;
		}

		printf("csid=%s,count=%d,aus=%d\n",session_id, count++, audio_stat);
		err_code = QIVWAudioWrite(session_id, (const void *)&audio_buffer[audio_count], len, audio_stat);
		if (MSP_SUCCESS != err_code)
		{
			printf("QIVWAudioWrite failed! error code:%d\n",err_code);
			_snprintf(sse_hints, sizeof(sse_hints), "QIVWAudioWrite errorCode=%d", err_code);
			goto exit;
		}
		if (MSP_AUDIO_SAMPLE_LAST == audio_stat)
		{
			break;
		}
		audio_count += len;
		audio_size -= len;

		sleep_ms(200); //ģ����˵��ʱ���϶��10֡����Ƶʱ��Ϊ200ms
	}
	_snprintf(sse_hints, sizeof(sse_hints), "success");

exit:
	if (NULL != session_id)
	{
		QIVWSessionEnd(session_id, sse_hints);
	}
	if (NULL != f_aud)
	{
		fclose(f_aud);
	}
	if (NULL != audio_buffer)
	{
		free(audio_buffer);
	}
}


//��˷�¼��demo
void ivw_demo_microphone(const char *grammar_list, const char* session_begin_params)
{
	const char *session_id = NULL;
	int err_code = MSP_SUCCESS;
	long audio_size = 0;
	long audio_count = 0;
	int count = 0;
	int audio_stat = MSP_AUDIO_SAMPLE_CONTINUE;
	char sse_hints[128];
	DWORD bufsize;
	long len =0;

	HWAVEIN hWaveIn;  //�����豸
	WAVEFORMATEX waveform; //�ɼ���Ƶ�ĸ�ʽ���ṹ��
	BYTE *pBuffer;//�ɼ���Ƶʱ�����ݻ���
	WAVEHDR wHdr; //�ɼ���Ƶʱ�������ݻ���Ľṹ��
	HANDLE          wait;

	waveform.wFormatTag = WAVE_FORMAT_PCM;//������ʽΪPCM
	waveform.nSamplesPerSec = 16000;//��Ƶ������
	waveform.wBitsPerSample = 16;//��������
	waveform.nChannels = 1;//����������
	waveform.nAvgBytesPerSec = 16000;//ÿ���������
	waveform.nBlockAlign = 2;//һ����Ĵ�С������bit���ֽ�������������
	waveform.cbSize = 0;//һ��Ϊ0

	wait = CreateEvent(NULL, 0, 0, NULL);
	//ʹ��waveInOpen����������Ƶ�ɼ�
	waveInOpen(&hWaveIn, WAVE_MAPPER, &waveform, (DWORD_PTR)wait, 0L, CALLBACK_EVENT);

	bufsize= 1024 * 500;//�����ʵ���С���ڴ�洢��Ƶ���ݣ����ʵ������ڴ��С������¼��ʱ�䣬���ȡ�������ڴ������

	session_id = QIVWSessionBegin(grammar_list, session_begin_params, &err_code);
	if (err_code != MSP_SUCCESS)
	{
		printf("QIVWSessionBegin failed! error code:%d\n", err_code);
		goto exit;
	}

	err_code = QIVWRegisterNotify(session_id, cb_ivw_msg_proc, NULL);
	if (err_code != MSP_SUCCESS)
	{
		_snprintf(sse_hints, sizeof(sse_hints), "QIVWRegisterNotify errorCode=%d", err_code);
		printf("QIVWRegisterNotify failed! error code:%d\n", err_code);
		goto exit;
	}

	pBuffer = malloc(bufsize);
	wHdr.lpData = (LPSTR)pBuffer;
	wHdr.dwBufferLength = bufsize;
	wHdr.dwBytesRecorded = 0;
	wHdr.dwUser = 0;
	wHdr.dwFlags = 0;
	wHdr.dwLoops = 1;
	waveInPrepareHeader(hWaveIn, &wHdr, sizeof(WAVEHDR));//׼��һ���������ݿ�ͷ����¼��
	waveInAddBuffer(hWaveIn, &wHdr, sizeof(WAVEHDR));//ָ���������ݿ�Ϊ¼�����뻺��
	waveInStart(hWaveIn);//��ʼ¼��

	//while (audio_count< bufsize && wakeupFlage!=1)//���λ���
	while (audio_count< bufsize)//��������
	{
		Sleep(200);//�ȴ�����¼��5s

		len = 10 * FRAME_LEN; //16k��Ƶ��10֡ ��ʱ��200ms��
		audio_stat = MSP_AUDIO_SAMPLE_CONTINUE;
		if (audio_count >= wHdr.dwBytesRecorded)
		{
			len = audio_size;
			audio_stat = MSP_AUDIO_SAMPLE_LAST; //���һ��
		}
		if (0 == audio_count)
		{
			audio_stat = MSP_AUDIO_SAMPLE_FIRST;
		}

		printf("csid=%s,count=%d,aus=%d\n", session_id, count++, audio_stat);
		err_code = QIVWAudioWrite(session_id, (const void *)&pBuffer[audio_count], len, audio_stat);
		if (MSP_SUCCESS != err_code)
		{
			printf("QIVWAudioWrite failed! error code:%d\n", err_code);
			_snprintf(sse_hints, sizeof(sse_hints), "QIVWAudioWrite errorCode=%d", err_code);
			goto exit;
		}
		if (MSP_AUDIO_SAMPLE_LAST == audio_stat)
		{
			break;
		}
		audio_count += len;
	}
	waveInReset(hWaveIn);//ֹͣ¼��
	if (NULL != pBuffer) 
	{
		free(pBuffer);
	}
	_snprintf(sse_hints, sizeof(sse_hints), "success");

exit:
	if (NULL != session_id)
	{
		QIVWSessionEnd(session_id, sse_hints);
	}

}

int main(int argc, char* argv[])
{
	int         ret       = MSP_SUCCESS;
	const char *lgi_param = "appid = 316e9b7a, work_dir = .";
	const char *ssb_param = "ivw_threshold=0:1450,sst=wakeup,ivw_res_path =fo|res/ivw/wakeupresource.jet";
	int aud_src = 0;
	/* �û���¼ */
	ret = MSPLogin(NULL, NULL, lgi_param); //��һ���������û������ڶ������������룬�����������ǵ�¼�������û������������http://www.xfyun.cnע���ȡ
	if (MSP_SUCCESS != ret)
	{
		printf("MSPLogin failed, error code: %d.\n", ret);
		goto exit ;//��¼ʧ�ܣ��˳���¼
	}
	printf("\n###############################################################################################################\n");
	printf("## ivw_demo_microphone Ϊʹ����˷���л��ѵ�demo,run_ivwΪʹ����Ƶ�ļ����ѵ�demo����ѡ������һ�ַ�ʽ���л���##\n");
	printf("## ��ע�⣬��ʹ��run_ivw����������Ҫ���ݻ��Ѵ���������¼�Ʋ�������Ϊ��IVW_AUDIO_FILE_NAME��ָ�����ƣ������bin/audio�ļ���##\n");
	printf("###############################################################################################################\n\n");
	
	printf("��Ƶ��������? \n0: ���ļ�����\n1:��MIC˵��\n");
	scanf("%d", &aud_src);
	if (aud_src) 
	{
		ivw_demo_microphone(NULL, ssb_param);
	}
	else
	{
		run_ivw(NULL, IVW_AUDIO_FILE_NAME, ssb_param);  
	}

	sleep_ms(2000);
exit:
	printf("��������˳� ...\n");
	_getch();
	MSPLogout(); //�˳���¼
	return 0;
}
