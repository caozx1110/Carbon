/*
* �������弼���ܹ���������дҵ���е����ݽ������������
*/

#include <stdlib.h>
#include <stdio.h>
#include <windows.h>
#include <conio.h>
#include <errno.h>
#include <math.h>
#include <locale.h>

#include "qisr.h"
#include "msp_cmn.h"
#include "msp_errors.h"
#include "json.h"


#ifdef _WIN64
#pragma comment(lib,"../../libs/msc_x64.lib") //x64
#else
#pragma comment(lib,"../../libs/msc.lib") //x86
#endif

#define	BUFFER_SIZE	4096
#define FRAME_LEN	640 
#define HINTS_SIZE  100

void U8toGBK(char u8str[])
{
	int len_wchart;
	wchar_t *unicode_2;
	int len_gbk;
	char *gbkstr;
	len_wchart = MultiByteToWideChar(CP_UTF8,0,u8str,-1,NULL,0); 
	unicode_2 = (wchar_t *)malloc(len_wchart*sizeof(wchar_t));
	MultiByteToWideChar(CP_UTF8,0,u8str,-1,unicode_2,len_wchart);
	len_gbk = WideCharToMultiByte(CP_ACP,0,unicode_2,-1,NULL,0,NULL,NULL);
	gbkstr = (char*)malloc(len_gbk);
	WideCharToMultiByte(CP_ACP,0,unicode_2,-1,gbkstr,len_gbk,NULL,NULL);  

	free(unicode_2);
	printf("\n\n%s\n",gbkstr);
}

int json_pase(char * rec_result)
{
	enum json_error error;
	json_t * root          = NULL;
	json_t * resultjson    = NULL;
	json_t * sub_result    = NULL; 
	char   * originalstr   = NULL;
	int      ret           = 0;
	error = json_parse_document(&root,rec_result);
	if (error!=JSON_OK)
	{
		printf("\njson_parse_document failed, error code: %d\n", error);
		goto json_error;
	}
	resultjson = json_find_first_label(root,"trans_result");
	if (resultjson == NULL)
	{
		resultjson = json_find_first_label(root,"errmsg");
		if (resultjson!=NULL&&resultjson->child!=NULL)
		{
			originalstr = resultjson->child->text;
			printf("\n\n%s\n",originalstr);
		}
		else
		{
			printf("\njson_find_first_label failed,\"error\" not found\n");
			goto json_error;
		}
	}
	else
	{
		sub_result = json_find_first_label(resultjson->child,"dst");
		originalstr = sub_result->child->text;
		U8toGBK(originalstr);
	}
	goto json_exit;

json_error:
	ret = -1;

json_exit:
	if (root!=NULL)
	{
		json_free_value(&root);
		root = NULL;
	}
	return ret;
}

void run_iat(const char* audio_file, const char* session_begin_params)
{
	const char*		session_id					=	NULL;
	char			*rec_result		            =	NULL;	
	char			hints[HINTS_SIZE]			=	{NULL}; //hintsΪ�������λỰ��ԭ�����������û��Զ���
	unsigned int	total_len					=	0; 
	int				aud_stat					=	MSP_AUDIO_SAMPLE_CONTINUE ;		//��Ƶ״̬
	int				ep_stat						=	MSP_EP_LOOKING_FOR_SPEECH;		//�˵���
	int				rec_stat					=	MSP_REC_STATUS_SUCCESS ;		//ʶ��״̬
	int				errcode						=	MSP_SUCCESS ;

	FILE*			f_pcm						=	NULL;
	char*			p_pcm						=	NULL;
	long			pcm_count					=	0;
	long			pcm_size					=	0;
	long			read_size					=	0;
	
	if (NULL == audio_file)
		goto iat_exit;

	f_pcm = fopen(audio_file, "rb");
	if (NULL == f_pcm) 
	{
		printf("\nopen [%s] failed! \n", audio_file);
		goto iat_exit;
	}
	
	fseek(f_pcm, 0, SEEK_END);
	pcm_size = ftell(f_pcm); //��ȡ��Ƶ�ļ���С 
	fseek(f_pcm, 0, SEEK_SET);		

	p_pcm = (char *)malloc(pcm_size);
	if (NULL == p_pcm)
	{
		printf("\nout of memory! \n");
		goto iat_exit;
	}

	read_size = fread((void *)p_pcm, 1, pcm_size, f_pcm); //��ȡ��Ƶ�ļ�����
	if (read_size != pcm_size)
	{
		printf("\nread [%s] error!\n", audio_file);
		goto iat_exit;
	}
	
	session_id = QISRSessionBegin(NULL, session_begin_params, &errcode); //��д����Ҫ�﷨����һ������ΪNULL
	if (MSP_SUCCESS != errcode)
	{
		printf("\nQISRSessionBegin failed! error code:%d\n", errcode);
		goto iat_exit;
	}
	
	rec_result = (char*)malloc(BUFFER_SIZE);
	memset(rec_result,0,BUFFER_SIZE);

	while (1) 
	{
		unsigned int len = 10 * FRAME_LEN; // ÿ��д��200ms��Ƶ(16k��16bit)��1֡��Ƶ20ms��10֡=200ms��16k�����ʵ�16λ��Ƶ��һ֡�Ĵ�СΪ640Byte
		int ret = 0;

		if (pcm_size < 2 * len) 
			len = pcm_size;
		if (len <= 0)
			break;

		aud_stat = MSP_AUDIO_SAMPLE_CONTINUE;
		if (0 == pcm_count)
			aud_stat = MSP_AUDIO_SAMPLE_FIRST;

		printf(">");
		ret = QISRAudioWrite(session_id, (const void *)&p_pcm[pcm_count], len, aud_stat, &ep_stat, &rec_stat);
		if (MSP_SUCCESS != ret)
		{
			printf("\nQISRAudioWrite failed! error code:%d\n", ret);
			goto iat_exit;
		}
			
		pcm_count += (long)len;
		pcm_size  -= (long)len;
		
		if (MSP_REC_STATUS_SUCCESS == rec_stat) //�Ѿ��в�����д���
		{
			const char *rslt = QISRGetResult(session_id, &rec_stat, 0, &errcode);
			if (MSP_SUCCESS != errcode)
			{
				printf("\nQISRGetResult failed! error code: %d\n", errcode);
				goto iat_exit;
			}
			if (NULL != rslt)
			{
				unsigned int rslt_len = strlen(rslt);
				total_len += rslt_len;
				if (total_len >= BUFFER_SIZE)
				{
					printf("\nno enough buffer for rec_result !\n");
					goto iat_exit;
				}
				strncat(rec_result, rslt, rslt_len);
			}
		}

		if (MSP_EP_AFTER_SPEECH == ep_stat)
			break;
		Sleep(200); //ģ����˵��ʱ���϶��200ms��Ӧ10֡����Ƶ
	}
	errcode = QISRAudioWrite(session_id, NULL, 0, MSP_AUDIO_SAMPLE_LAST, &ep_stat, &rec_stat);
	if (MSP_SUCCESS != errcode)
	{
		printf("\nQISRAudioWrite failed! error code:%d \n", errcode);
		goto iat_exit;	
	}

	while (MSP_REC_STATUS_COMPLETE != rec_stat) 
	{
		const char *rslt = QISRGetResult(session_id, &rec_stat, 0, &errcode);
		if (MSP_SUCCESS != errcode)
		{
			printf("\nQISRGetResult failed, error code: %d\n", errcode);
			goto iat_exit;
		}
		if (NULL != rslt)
		{
			unsigned int rslt_len = strlen(rslt);
			total_len += rslt_len;
			if (total_len >= BUFFER_SIZE)
			{	
				rec_result = (char*)realloc(rec_result,total_len);
				if (rec_result==NULL)
				{
					printf("\nno enough buffer for rec_result !\n");
					goto iat_exit;
				}
			}
			strncat(rec_result, rslt, rslt_len);
		}
		Sleep(150); //��ֹƵ��ռ��CPU
	}
	errcode = json_pase(rec_result);
	if (errcode!=0)
	{
		printf("json_pase failed ,errcode is %d\n",errcode);
	}

iat_exit:
	if (NULL != f_pcm)
	{
		fclose(f_pcm);
		f_pcm = NULL;
	}
	if (NULL != p_pcm)
	{	free(p_pcm);
		p_pcm = NULL;
	}
	if (rec_result!=NULL)
	{
		free(rec_result);
		rec_result = NULL;
	}
	QISRSessionEnd(session_id, hints);
}

int main(int argc, char* argv[])
{
	int			ret						=	MSP_SUCCESS;
	int			upload_on				=	1; //�Ƿ��ϴ��û��ʱ�
	const char* login_params			=	"appid = 316e9b7a"; // ��¼������appid��msc���,��������Ķ�


	/*
	* sub:				����ҵ������
	* domain:			����
	* language:			����
	* accent:			����
	* sample_rate:		��Ƶ������
	* result_type:		ʶ������ʽ
	* result_encoding:	��������ʽ
	*
	* nlp_version:      ����汾
	* sch:              �Ƿ�ʹ�������ʶ
	*/
	const char* session_begin_params ="trssrc=its,addcap = translate,orilang = en,translang = cn,sch=1,sub=iat,domain = iat, language = zh_cn, accent = mandarin,aue = speex-wb;7, sample_rate = 16000";

	

	/* �û���¼ */
	ret = MSPLogin(NULL, NULL, login_params); //��һ���������û������ڶ������������룬����NULL���ɣ������������ǵ�¼����	
	if (MSP_SUCCESS != ret)
	{
		printf("MSPLogin failed , Error code %d.\n",ret);
		goto exit; //��¼ʧ�ܣ��˳���¼
	}
	run_iat("wav/weather.pcm", session_begin_params);


exit:
	printf("\n��������˳� ...\n");
	_getch();
	MSPLogout(); //�˳���¼

	return 0;
}
